from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import connections
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from decimal import Decimal
import json
import requests
import hashlib
import base64
import subprocess

#获取信用评分
def get_wallet_address(wallet_address):
    if not wallet_address:
       result_content = {
          "code": 1,
           "message": "wallet_address is required'"
       }
       return JsonResponse(result_content)

    url = 'https://credit.tagfusion.org/predict'
    response = requests.post(url, json={'wallet_address': wallet_address})

    if response.status_code != 200:
        result_content = {
            "code": 1,
            "message": "API request failed"
        }
        return JsonResponse(result_content)
    # 返回解析后的 JSON 响应
    return response.json()


#计算利率
def compute_interest_rate(credit_score):
       if credit_score is None:
           return JsonResponse({'status': 'error', 'message': 'credit_score is required'}, status=400)

       # 常量参数
       BASE_RATE = 0.05  # 5%
       MAX_APY = 0.25  # 25%
       MAX_CREDIT_SCORE = 850
       MIN_CREDIT_SCORE = 300

       # 确保信用评分在有效范围内
       if credit_score < MIN_CREDIT_SCORE:
           MAX_APY = 0.25


       if credit_score > MAX_CREDIT_SCORE:
           BASE_RATE = 0.05

       # 计算风险溢价
       risk_premium = (MAX_APY - BASE_RATE) * (MAX_CREDIT_SCORE - credit_score) / (MAX_CREDIT_SCORE - MIN_CREDIT_SCORE)

       # 计算最终年化利率
       apy = round(BASE_RATE + risk_premium, 4)

       return apy

#根据信用计算借款金额
def calculate_loan_amount(credit_score, min_score=0, max_score=1000, min_loan=10000, max_loan=1000000):
    # 确保信用评分在有效范围内
    if credit_score < min_score:
        credit_score = min_score
    elif credit_score > max_score:
        credit_score = max_score

    # 归一化信用评分
    normalized_score = (credit_score - min_score) / (max_score - min_score)

    # 计算借款金额
    loan_amount = min_loan + normalized_score * (max_loan - min_loan)

    return loan_amount

#将tags转换为utags
def convert_to_utura(amount):
    return int(amount * 100000000)  # 1 tags = 100000000 utags

#将utags转换为tags
def convert_to_tura(amount):
    return amount / 100000000  # 1 tags = 100000000 utags

#获取用户贷款信息
def account_loan_info(request):
    if request.method == 'GET':
        address = request.GET.get('address')

    if not address:
        result_content = {
            "code": 1,
            "message": "Address is required"
        }
        return JsonResponse(result_content)

    #获取信用
    api_response = get_wallet_address(address)
    credit_score = api_response.get('credit_score')

    #获取利率
    # apy = compute_interest_rate(credit_score)
    apy = 0
    #计算借款
    min_loan = 10000
    loan_amount = calculate_loan_amount(credit_score)

    result_content = {
        "code": 0,
        "message": {
            "data":{
                "credit_score" : credit_score,
                "borrow_APY": apy,
                "max_loan_amount": loan_amount,
                "min_loan_amount": min_loan,
            }
        }
    }
    return JsonResponse(result_content)

#转账（
# 系统命令  转账:wasmd tx bank send demo tura12g2up77ngna09a3cvcwra3yajy3zhuw7mlrqyx 1000000utags --from demo --fees 30000utura --chain-id mainnet-tura --keyring-backend test -y
#         只能先添加用户才能在转账时候指定账户 添加用户：echo "repair stable logic wisdom donor gun chuckle else used culture spider tube logic myth axis dove awesome away save dizzy slow cute shuffle invite" | wasmd keys add demo --keyring-backend test --recover
# ）
def create_transfer(to_address, currency, loan_amount):
    if not to_address or not currency or not loan_amount:
        result_content = {
            "code": 1,
            "message": "Missing required fields"
        }
        return JsonResponse(result_content)


    sender = "demo"  # 发送者地址
    fees = "18000"  # 设置固定费用
    chain_id = "mainnet-tura"  # 链 ID

    # 调用转换方法
    loan_amount_utura = convert_to_utura(loan_amount)

    # 构建命令
    command = [
        "wasmd", "tx", "bank", "send", sender, to_address,
        f"{int(loan_amount_utura)} utags", "--from", sender,
        f"--fees={fees} utura", f"--chain-id={chain_id}",
        "--keyring-backend", "test", "-y"
    ]

    try:
        # 使用 Popen 执行命令
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return {
                "code": 1,
                "message": "Transfer failed",
                "error": stderr.decode('utf-8')
            }

        return {
            "code": 0,
            "message": "Transfer successful",
            "output": stdout.decode('utf-8')
        }
    except Exception as e:
        return {
            "code": 1,
            "message": "Transfer error",
            "error": str(e)
        }

#借款
def create_loan(request):
    if request.method == 'POST':
        to_address = request.POST.get('address')  # 借款方地址
        currency = request.POST.get('currency')  # 币种
        interest_rate = request.POST.get('borrow_APY')  # 利率（借款APY）
        loan_amount = request.POST.get('loan_amount')  # 借款金额
        repayment_days = request.POST.get('repayment_date')  # 还款天数
        from_address = "tura12g2up77ngna09a3cvcwra3yajy3zhuw7mlrqyx"  # 贷款方地址

        # 数据验证
        if not to_address or not interest_rate or not loan_amount or not repayment_days or not currency:
            result_content = {
                "code": 1,
                "message": "parameter is required"
            }
            return JsonResponse(result_content)

        try:
            # 将利率、金额、还款天数转换为合适的类型
            interest_rate = float(interest_rate)
            loan_amount = float(loan_amount)
            repayment_days = int(repayment_days)  # 确保还款天数被正确转换为整数
        except ValueError:
            result_content = {
                "code": 1,
                "message": "Invalid data format"
            }
            return JsonResponse(result_content)

        min_loan_amount = 10000  # 设置最小借款金额
        max_loan_amount = 1000000  # 设置最大借款金额

        # 判断借款金额是否在范围内
        if loan_amount < min_loan_amount or loan_amount > max_loan_amount:
            result_content = {
                "code": 1,
                "message": f"loan_amount must be between {min_loan_amount} and {max_loan_amount}"
            }
            return JsonResponse(result_content)

        # 检查借款方是否有未还清的贷款
        try:
            with connections['tagfusion'].cursor() as cursor:
                cursor.execute("""
                           SELECT COUNT(*)
                           FROM public.loan_records
                           WHERE to_address = %s AND status IN (1, 2, 4)  -- 状态为未到期、到期未还或部分还款
                       """, [to_address])
                existing_loan_count = cursor.fetchone()[0]

            if existing_loan_count > 0:
                # 如果存在未还清贷款，禁止借款
                result_content = {
                    "code": 1,
                    "message": "Outstanding loan exists, new loan is not allowed"
                }
                return JsonResponse(result_content)
        except Exception as e:
            result_content = {
                "code": 1,
                "message": str(e)
            }
            return JsonResponse(result_content)

        loan_start_date = datetime.now()

        try:
            # 确保 repayment_days 是整数，并计算还款日期
            repayment_date = loan_start_date + timedelta(days=repayment_days)
        except TypeError as e:
            result_content = {
                "code": 1,
                "message": f"Invalid repayment days: {str(e)}"
            }
            return JsonResponse(result_content)

        # 进行转账操作
        transfer_result = create_transfer(to_address, currency, loan_amount)

        loan_amount_utura = convert_to_utura(loan_amount)

        # 从 output 中提取 code 和 info
        output_lines = transfer_result["output"].split("\n")
        output_code = None
        error_message = ""

        for line in output_lines:
            if line.startswith("code:"):
                output_code = int(line.split(":")[1].strip())
            elif line.startswith("info:"):
                error_message = line.split(":")[1].strip()

        if output_code == 0:
            try:
                with connections['tagfusion'].cursor() as cursor:
                    cursor.execute("""
                               INSERT INTO public.loan_records (from_address, to_address, loan_amount, interest_rate, loan_start_date, repayment_date, status, currency)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                               RETURNING id
                           """, [
                        from_address,
                        to_address,
                        loan_amount_utura,
                        interest_rate,
                        loan_start_date,
                        repayment_date,
                        1,  # 初始状态
                        currency
                    ])
                    loan_record_id = cursor.fetchone()[0]  # 获取插入记录的 ID

                result_content = {
                    "code": 0,
                    "message": "Loan created successfully",
                    "loan_id": loan_record_id  # 返回插入的贷款记录 ID
                }
            except Exception as e:
                result_content = {
                    "code": 1,
                    "message": f"Failed to insert loan record: {str(e)}"
                }
        else:
            result_content = {
                "code": 1,
                "message": "Transfer failed: " + error_message
            }

        return JsonResponse(result_content)


#账单
def loan_list(request):
    if request.method == 'GET':
        address = request.GET.get('address')
        page = int(request.GET.get('page', 1))  # 默认第1页
        page_size = int(request.GET.get('page_size', 10))  # 默认每页10条记录

        if not address:
            result_content = {
                "code": 1,
                "message": "Address is required"
            }
            return JsonResponse(result_content)

        try:
            current_datetime = datetime.now()

            with connections['tagfusion'].cursor() as cursor:
                cursor.execute("""
                               SELECT id, loan_start_date, repayment_date, interest_rate, loan_amount, total_repayment_amount, currency, status
                               FROM public.loan_records
                               WHERE to_address = %s
                               ORDER BY (status = '3'), loan_start_date DESC
                           """, [address])

                rows = cursor.fetchall()

            loans = []
            for row in rows:
                loan_id = row[0]
                loan_start_date = row[1]
                repayment_date = row[2]
                interest_rate = row[3]
                loan_amount = row[4]
                total_repayment_amount = row[5]
                currency = row[6]
                status = row[7]

                # 计算经过的天数
                days_passed = (current_datetime - loan_start_date).days

                if status == '3':  # 部分还款
                    # 计算实际未还款金额
                    remaining_amount = loan_amount - total_repayment_amount
                    interest_amount = remaining_amount * interest_rate * days_passed if days_passed >= 0 else 0.0
                else:  # 全部未还款
                    interest_amount = loan_amount * interest_rate * days_passed if days_passed >= 0 else 0.0

                # 计算总金额时减去已还款部分
                total_amount = loan_amount + interest_amount - total_repayment_amount

                # 更新数据库中的利息金额
                with connections['tagfusion'].cursor() as cursor:
                    cursor.execute("""
                            UPDATE public.loan_records
                            SET interest_amount = %s
                            WHERE id = %s
                        """, [interest_amount, loan_id])

                # 将 loan_amount 转换为 tura
                loan_amount_tura = convert_to_tura(loan_amount)

                loans.append({
                    "id": loan_id,
                    "repayment_date": repayment_date.isoformat() if repayment_date else None,
                    "borrow_APY": float(interest_rate),
                    "loan_amount": float(loan_amount_tura),
                    "currency": currency,
                    "interest_amount": float(convert_to_tura(interest_amount)),  # 返回 interest_amount 以 tura
                    "amount": float(convert_to_tura(total_amount)),  # 返回 total_amount 以 tura
                    "status": status
                })

            # 分页处理
            paginator = Paginator(loans, page_size)
            loans_page = paginator.get_page(page)

            result_content = {
                "code": 0,
                "loans": list(loans_page),  # 转换为列表
                "total_pages": paginator.num_pages,
                "current_page": loans_page.number,
                "total_items": paginator.count,
            }

        except Exception as e:
            result_content = {
                "code": 1,
                "message": str(e)
            }

        return JsonResponse(result_content)

    return JsonResponse({"code": 1, "message": "Invalid request method"})

#账单详情
def loan_list_details(request):
    if request.method == 'GET':
        loan_id = request.GET.get('id')  # 获取贷款 ID

        if not loan_id:
            result_content = {
                "code": 1,
                "message": "Loan ID is required"
            }
            return JsonResponse(result_content)

        try:
            with connections['tagfusion'].cursor() as cursor:
                cursor.execute("""
                       SELECT id, repayment_date, interest_rate, loan_amount, currency, interest_amount
                       FROM public.loan_records
                       WHERE id = %s
                   """, [loan_id])

                row = cursor.fetchone()  # 使用 fetchone 只获取一条记录

            if row is None:
                return JsonResponse({"code": 1, "message": "Loan not found"})

            loan_id = row[0]
            repayment_date = row[1]
            interest_rate = row[2]
            loan_amount = row[3]
            currency = row[4]
            interest_amount = row[5]

            # 计算总金额并转换为 tura
            total_amount = loan_amount + interest_amount

            result_content = {
                "code": 0,
                "loan": {
                    "id": loan_id,
                    "repayment_date": repayment_date.isoformat() if repayment_date else None,
                    "borrow_APY": float(interest_rate),
                    "loan_amount": float(convert_to_tura(loan_amount)),  # 返回 utags
                    "currency": currency,
                    "interest_amount": float(convert_to_tura(interest_amount)),  # 返回 interest_amount 以 utags
                    "amount": float(convert_to_tura(total_amount)),  # 返回 total_amount 以 utags
                }
            }

        except Exception as e:
            result_content = {
                "code": 1,
                "message": str(e)
            }

        return JsonResponse(result_content)

    return JsonResponse({"code": 1, "message": "Invalid request method"})

#还款
def repay(request):
    # 处理 POST 请求
    if request.method == 'POST':
        loan_id = request.POST.get('id')
        address = request.POST.get('address')
        repay_amount = request.POST.get('repay_amount')
        from_address = "tura12g2up77ngna09a3cvcwra3yajy3zhuw7mlrqyx"  # 固定的贷款方地址

        # 参数检查
        if not loan_id or not address or not repay_amount:
            return JsonResponse({"code": 1, "message": "Loan ID, address, and repay amount are required"})

        try:
            repay_amount = Decimal(repay_amount) * 100000000  # 转换为 utags

            sql_query = """
                            SELECT COUNT(*)
                            FROM public.transaction
                            WHERE memo LIKE %s
                              AND success = true
                        """
            query_param = [f'%"loan_id":{loan_id}%']

            with connections['default'].cursor() as cursor:
                cursor.execute(sql_query, query_param)

                result = cursor.fetchone()
                tx_count = result[0] if result else 0  # 检查查询结果是否为 None

            if tx_count == 0:
                return JsonResponse({"code": 1, "message": "No successful repayment transaction found with the loan ID in memo"})

            # 查询该 loan_id 的贷款记录
            with connections['tagfusion'].cursor() as cursor:
                cursor.execute("""
                    SELECT id, loan_amount, total_repayment_amount
                    FROM public.loan_records
                    WHERE id = %s
                """, [loan_id])

                rows = cursor.fetchall()

            if not rows:
                return JsonResponse({"code": 1, "message": "No loan record found with the provided loan ID"})

            # 提取查询结果
            loan_record = rows[0]
            loan_id = loan_record[0]
            loan_amount = loan_record[1]
            total_repayment_amount = loan_record[2]

            # 计算新的还款总额
            new_repayment_amount = total_repayment_amount + repay_amount

            # 如果还款已满，更新状态为已还清，否则为部分还款
            if new_repayment_amount >= loan_amount:
                new_repayment_amount = loan_amount
                new_status = 3  # 已还清
            else:
                new_status = 4  # 部分还款

            # 更新贷款记录中的还款信息
            with connections['tagfusion'].cursor() as cursor:
                cursor.execute("""
                    UPDATE public.loan_records
                    SET repayment_count = repayment_count + 1,
                        total_repayment_amount = %s,
                        status = %s
                    WHERE id = %s
                """, [new_repayment_amount, new_status, loan_id])

            result_content = {
                "code": 0,
                "message": "Repayment successful",
                "data": {
                    "status": new_status
                }
            }

        except Exception as e:
            result_content = {
                "code": 1,
                "message": str(e)
            }

        return JsonResponse(result_content)

    return JsonResponse({"code": 1, "message": "Invalid request method"})


