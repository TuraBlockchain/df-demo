from django.http import JsonResponse
from django.db import connections
from django.http import HttpResponse
import sys
import requests
import json
from datetime import datetime
import uuid

#获取上链数据
# 定义多个标签，如果以后需要添加更多标签，可以在这个数组中添加
LABELS = ["Solana"]

def get_nft_data(request):
    # 从 GET 参数中获取 wallet_address
    wallet_address = request.GET.get('walletAddress')

    if not wallet_address:
        result_content = {
            "code": 1,
            "message": "钱包地址是必需的"
        }
        return JsonResponse(result_content)

    # Magic Eden API 基础 URL
    base_url = "https://api-mainnet.magiceden.dev/v2"

    # 获取钱包中的所有 NFT 的 mint 地址
    wallet_nfts_url = f"{base_url}/wallets/{wallet_address}/tokens"
    try:
        wallet_nfts_response = requests.get(wallet_nfts_url)
        wallet_nfts_response.raise_for_status()

        # 解析 Magic Eden 返回的 JSON 数据
        wallet_nfts_data = wallet_nfts_response.json()

        # 如果没有找到任何 NFT
        if not wallet_nfts_data:
            result_content = {
                "code": 1,
                "message": "该钱包没有持有任何 NFT"
            }
            return JsonResponse(result_content)

        # 提取 mint 地址列表
        mint_addresses = [nft["mintAddress"] for nft in wallet_nfts_data]

        # 获取 Magic Eden API 密钥
        api_key = "155bc2f5-be8c-4788-a4e4-6d78a7c17be1"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # 生成一个随机的 UUID
        request_uuid = str(uuid.uuid4())
        MAX_RESPONSE_SIZE = 3000  # 最大字节大小限制

        # 初始化返回数据
        result_json = {
            "code": 0,
            "message": "请求成功",
            "data": {
                "nfts": [],
                "uuid": request_uuid,  # 将 UUID 添加到返回的数据中
                "type": ["Solana"]  # 假设你用 Solana 作为类型
            }
        }

        # 查询每个 mint 地址的销售信息
        for mint_address in mint_addresses:
            nft_info_url = f"{base_url}/tokens/{mint_address}"
            nft_listings_url = f"{base_url}/tokens/{mint_address}/listings"
            nft_activities_url = f"{base_url}/tokens/{mint_address}/activities"

            # 发起请求获取 NFT 信息
            nft_info_response = requests.get(nft_info_url, headers=headers)
            nft_info_response.raise_for_status()

            nft_listings_response = requests.get(nft_listings_url, headers=headers)
            nft_listings_response.raise_for_status()

            nft_activities_response = requests.get(nft_activities_url, headers=headers)
            nft_activities_response.raise_for_status()

            # 解析响应数据
            nft_info_data = nft_info_response.json()
            nft_listings_data = nft_listings_response.json()  # 获取所有的 listing 数据
            nft_activities_data = nft_activities_response.json()  # 获取所有的 activity 数据

            # 筛选 name 为 "STEPNNFT" 的 NFT，忽略大小写
            nft_name = nft_info_data.get('name', '').lower()

            # 计算该钱包持有该 NFT 的天数
            wallet_holding_days = None
            if isinstance(nft_activities_data, list):
                first_activity = next(
                    (activity for activity in nft_activities_data if activity.get("type") == "LIST"), None)
                if first_activity:
                    first_activity_time = first_activity.get("blockTime")
                    if first_activity_time:
                        first_activity_datetime = datetime.utcfromtimestamp(first_activity_time)
                        current_datetime = datetime.utcnow()
                        wallet_holding_period = current_datetime - first_activity_datetime
                        wallet_holding_days = wallet_holding_period.days

            # 限制 listings 数据最多为 5 个字典
            nft_activities_data = nft_activities_data[:3]

            # 将该 NFT 的信息添加到结果中
            result_json["data"]["nfts"].append({
                "nft_info": nft_info_data if nft_name == "stepnnft" else {},  # 只有符合条件的 nft_info 被加入
                "wallet_holding_days": wallet_holding_days,
                "listings": nft_listings_data,  # 完整的 listing 数据
                "activities": nft_activities_data,  # 完整的 activity 数据
            })

        # 检查返回结果的字节大小
        response_json = json.dumps(result_json)  # 转换为 JSON 字符串
        response_size = sys.getsizeof(response_json.encode('utf-8'))  # 获取字节大小

        if response_size > MAX_RESPONSE_SIZE:
            result_content = {
                "code": 1,
                "message": "响应数据超过最大字节限制"
            }
            return JsonResponse(result_content)

        # 返回最终结果
        return JsonResponse(result_json)

    except requests.exceptions.RequestException as e:
        # 捕获请求错误并返回错误信息
        result_json = {
            "code": 1,
            "message": f"API 请求失败: {str(e)}",
            "data": {
                "uuid": request_uuid,  # 将 UUID 添加到错误响应的 data 中
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
