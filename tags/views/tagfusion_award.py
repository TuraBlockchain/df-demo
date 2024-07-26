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
            select a.*
                  ,b.profile_image
            	  ,b.username
              from 
                (
                  select address
                        ,sum(register_award) register_award
                        ,sum(register_ct) register_ct
                        ,sum(verify_award) verify_award
                        ,sum(verify_ct) verify_ct
                        ,sum(invite_award) invite_award
                        ,sum(invite_ct) invite_ct
                        ,sum(total_award) total_award
                    from tagfusion_award_today 
                    where address = %s
                    group by address
            	) a 
            	full join (select address,profile_image,username from tags_cardinfo where address = %s) b 
                on a.address = b.address
            	;
            """, [address,address])
            tagfusion_award = cursor.fetchone()
            code = 1
            register_award = 0
            register_ct    = 0
            verify_award   = 0
            verify_ct      = 0
            invite_award   = 0
            invite_ct      = 0
            total_award    = 0
            profile_image = ""
            username = ""
            if tagfusion_award :
                code = 0
                register_award = tagfusion_award[1]
                register_ct    = tagfusion_award[2]
                verify_award   = tagfusion_award[3]
                verify_ct      = tagfusion_award[4]
                invite_award   = tagfusion_award[5]
                invite_ct      = tagfusion_award[6]
                total_award    = tagfusion_award[7]
                profile_image = tagfusion_award[8]
                username = tagfusion_award[9]
            #top50
            json_top50 = []
            cursor.execute("""
            select username
                  ,total_award
                  ,row_number() over(order by total_award desc)  raking
              from 
                (
                  select b.username
                        ,a.total_award
            		from 
                      (
                        select address
                              ,sum(total_award) total_award
                          from tagfusion_award_today
                          group by address 
                          order by total_award desc
                          limit 50
                      ) a 
                    left join tags_cardinfo b 
                    on a.address = b.address
                )t;
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
                "invite_award" : invite_award,
                "invite_ct" : invite_ct,
                "total_award" : total_award,
                "profile_image" : profile_image,
                "username" : username,
                "top50":json_top50
            }
            return JsonResponse(result_content)











