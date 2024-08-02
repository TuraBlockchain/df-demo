from django.http import JsonResponse
from django.shortcuts import render,redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import connections
import json
from collections import Counter
from tags.models import CardInfo,CardKV
from django.core.cache import cache

TAG_VERSION = 'tag1.0'
CACHE_KEYS_LIST = 'all_cache_keys'


@csrf_exempt
def get_award(request):
    if request.method == 'GET':
        address = request.GET.get('address')
        with connections['default'].cursor() as cursor:
            # select my tags
            cursor.execute("""
            select *
              from tagfusion_award_history
              where address = %s
            """, [address])
            tagfusion_award = cursor.fetchone()
            code = 1
            register_award = 0
            register_ct    = 0
            verify_award   = 0
            verify_ct      = 0
            invite_one_award   = 0
            invite_one_ct      = 0
            invite_two_award   = 0
            invite_two_ct      = 0
            invite_three_award = 0
            invite_three_ct = 0





            total_award    = 0
            profile_image = ""
            username = ""
            if tagfusion_award :
                code = 0
                register_award     = tagfusion_award[1]
                register_ct        = tagfusion_award[2]
                verify_award       = tagfusion_award[3]
                verify_ct          = tagfusion_award[4]
                invite_one_award   = tagfusion_award[5]
                invite_one_ct      = tagfusion_award[6]
                invite_two_award   = tagfusion_award[7]
                invite_two_ct      = tagfusion_award[8]
                invite_three_award = tagfusion_award[9]
                invite_three_ct = tagfusion_award[10]
                total_award    = tagfusion_award[11]
                profile_image = tagfusion_award[12]
                username = tagfusion_award[13]
            #top50
            json_top50 = []
            cursor.execute("""
            select * from tagfusion_award_history_top50;
            """)
            tagfusion_award_top50 = cursor.fetchall()
            if tagfusion_award_top50 :
                for row in tagfusion_award_top50:
                    json_top50.append({
                        "username": row[0],
                        "total_award": row[1],
                        "raking": row[2]
                    })
            result_content = 		{
                "code":code,
                "register_award":register_award,
                "register_ct" : register_ct,
                "verify_award" : verify_award,
                "verify_ct" : verify_ct,
                "invite_one_award"   :invite_one_award  ,
                "invite_one_ct"      :invite_one_ct     ,
                "invite_two_award"   :invite_two_award  ,
                "invite_two_ct"      :invite_two_ct     ,
                "invite_three_award" :invite_three_award,
                "invite_three_ct" :invite_three_ct,
                "total_award" : total_award,
                "profile_image" : profile_image,
                "username" : username,
                "top50":json_top50
            }
            return JsonResponse(result_content)











