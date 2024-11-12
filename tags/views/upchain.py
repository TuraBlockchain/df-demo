from django.http import JsonResponse
from django.db import connections
from django.http import HttpResponse
import requests
import json
from datetime import datetime
import uuid

#获取上链数据
def get_nft_data(request):
    # 从 GET 参数中获取 wallet_address 和 mint_address
    wallet_address = request.GET.get('nft_address')
    mint_address = request.GET.get('mint_address')

    if not wallet_address or not mint_address:
        result_content = {
            "code": 1,
            "message": "钱包地址和NFT地址是必需的"
        }
        return JsonResponse(result_content)

    # 构建 Magic Eden API 的请求 URL
    base_url = "https://api-mainnet.magiceden.dev/v2"

    # 获取单个NFT基础信息
    nft_info_url = f"{base_url}/tokens/{mint_address}"
    # 获取NFT当前挂单
    nft_listings_url = f"{base_url}/tokens/{mint_address}/listings"
    # 获取NFT交易历史
    nft_activities_url = f"{base_url}/tokens/{mint_address}/activities"
    # 获取钱包活动（即该钱包的交易历史）
    wallet_activities_url = f"{base_url}/wallets/{wallet_address}/activities"

    # 设置 API 密钥，替换成你获得的实际 API Key
    api_key = "155bc2f5-be8c-4788-a4e4-6d78a7c17be1"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # 生成一个随机的 UUID
    request_uuid = str(uuid.uuid4())

    try:
        # 发起并处理多个请求
        nft_info_response = requests.get(nft_info_url, headers=headers)
        nft_info_response.raise_for_status()

        nft_listings_response = requests.get(nft_listings_url, headers=headers)
        nft_listings_response.raise_for_status()

        nft_activities_response = requests.get(nft_activities_url, headers=headers)
        nft_activities_response.raise_for_status()

        wallet_activities_response = requests.get(wallet_activities_url, headers=headers)
        wallet_activities_response.raise_for_status()

        # 解析所有响应 JSON 数据
        nft_info_data = nft_info_response.json()
        nft_listings_data = nft_listings_response.json()
        nft_activities_data = nft_activities_response.json()
        wallet_activities_data = wallet_activities_response.json()

        wallet_first_activity_time = None

        # 获取钱包的首次活动时间（即该钱包首次购买NFT的时间）
        if wallet_activities_data:
            wallet_first_activity = next(
                (activity for activity in wallet_activities_data if activity.get("tokenMint") == mint_address), None)
            if wallet_first_activity:
                wallet_first_activity_time = wallet_first_activity.get("blockTime")

        wallet_holding_days = None
        if wallet_first_activity_time:
            wallet_first_activity_datetime = datetime.utcfromtimestamp(wallet_first_activity_time)
            current_datetime = datetime.utcnow()

            # 计算钱包持有时间
            wallet_holding_period = current_datetime - wallet_first_activity_datetime
            # 计算钱包持有天数
            wallet_holding_days = wallet_holding_period.days

        # 检查 nft_info_data 是否包含 Solana 的标签或信息
        solana_tag = "Solana"

        # 汇总结果数据，并添加 Solana 标签
        result_json = {
            "code": 0,
            "message": "请求成功",
            "data": {
                "nft_info": nft_info_data,
                "nft_listings": nft_listings_data,
                "nft_activities": nft_activities_data,
                # "wallet_activities_data":wallet_activities_data,
                "type": solana_tag,  # 添加 Solana 标签
                "wallet_holding_period_days": wallet_holding_days,  # 添加钱包持有NFT的天数
                "uuid": request_uuid  # 将 UUID 添加到 data 中
            }
        }

        return JsonResponse(result_json)

    except requests.exceptions.RequestException as e:
        # 捕获请求错误并返回错误信息
        result_json = {
            "code": 1,
            "message": f"API 请求失败: {str(e)}",
            "data": {
                "uuid": request_uuid  # 将 UUID 添加到错误响应的 data 中
            }
        }
        return JsonResponse(result_json, status=500)
#上链回执
def create_up_chain_data(request):
    if request.method == 'POST':
        address = request.POST.get('tura_address')  # 获取 tura_address
        data_json = request.POST.get('json')  # 获取 JSON 数据字符串
        uuid = request.POST.get('uuid')  # 获取 JSON 数据字符串

        # 数据验证
        if not address or not data_json:
            result_content = {
                "code": 1,
                "message": "parameter is required"
            }
            return JsonResponse(result_content)

        try:
            # 尝试解析传入的 JSON 数据字符串
            json_data = json.loads(data_json)  # 将 JSON 字符串转换为字典
        except json.JSONDecodeError:
            result_content = {
                "code": 1,
                "message": "Invalid JSON format in 'json' field"
            }
            return JsonResponse(result_content)

        # 从解析后的 JSON 中提取 'type' 字段
        data_type = json_data.get('type')

        if not data_type:
            result_content = {
                "code": 1,
                "message": "'type' field is missing in the provided JSON"
            }
            return JsonResponse(result_content)

        try:
            # 查询 transaction 表，检查 memo 中是否有含有 type 标签的 JSON 字符串，且 from_address 是否等于 address
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM public.transaction
                    WHERE
                        success = TRUE
                        AND memo LIKE %s  -- 使用 LIKE 检查 memo 中的 uuid 是否和传入的 uuid 一致
                """, [f'%"uuid":"{uuid}"%'])  # 将 uuid 插入到查询条件中
                # 获取符合条件的交易数量
                transaction_count = cursor.fetchone()[0]

            # 如果符合条件的交易存在，插入数据到 up_chain_data 表
            if transaction_count > 0:
                with connections['tagfusion'].cursor() as cursor:
                    # 插入数据到 up_chain_data 表
                    cursor.execute("""
                        INSERT INTO public.up_chain_data (address, type, json)
                        VALUES (%s, %s, %s)
                    """, [
                        address,
                        data_type,  # 插入 type 字段
                        json.dumps(json_data)  # 将字典转换为 JSON 字符串
                    ])
                result_content = {
                    "code": 0,
                    "message": "Data inserted successfully"
                }
            else:
                result_content = {
                    "code": 1,
                    "message": "No matching transaction found"
                }

        except Exception as e:
            result_content = {
                "code": 1,
                "message": f"Error occurred: {str(e)}"
            }

    return JsonResponse(result_content)

#获取简介信息
def get_chain_introduction(request):
    # 获取 GET 请求中的 id 参数
    introduction_id = request.GET.get('id')

    if not introduction_id:
        result_content = {
            "code": 1,
            "message": "'id' parameter is required"
        }
        return JsonResponse(result_content)

    try:
        # 根据传入的 id 查询 chain_Introduction 表中的数据
        with connections['tagfusion'].cursor() as cursor:
            cursor.execute("""
                SELECT id, type, Introduction
                FROM public.chain_Introduction
                WHERE id = %s
            """, [introduction_id])

            # 获取查询结果
            row = cursor.fetchone()

        if row:
            # 格式化查询结果（去掉 create_time 字段）
            data = {
                "id": row[0],
                "type": row[1],
                "Introduction": row[2]
            }
            result_content = {
                "code": 0,
                "message": "Data fetched successfully",
                "data": data
            }
        else:
            result_content = {
                "code": 1,
                "message": "Data not found"
            }

    except Exception as e:
        result_content = {
            "code": 1,
            "message": f"Error occurred: {str(e)}"
        }

    return JsonResponse(result_content)
