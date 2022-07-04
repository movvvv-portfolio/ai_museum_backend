from http.client import ResponseNotReady
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from article.models import Article as ArticleModel
from article.models import ArticleImage as ArticleImageModel

from article.serializers import ArticleSerializer
from django.utils import timezone

# 딥러닝 관련
# python
import os
import glob
import shutil
# import style_transfer
from style_transfer.main import style_transfer

# file manage(관리) 쉽게 도움 주는 라이브러리 https://docs.djangoproject.com/en/3.0/topics/files/
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# Create your views here.
class ArticleView(APIView):
    # 로그인 한 사용자의 게시글 목록 return
    # permission_classes =[permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [IsAdminOrIsAuthenticatedReadOnly]

    def get(self, request):
        articles = ArticleModel.objects.all()
        today = timezone.now()
        serializer = ArticleSerializer(articles, many=True).data

        # articles = ArticleModel.objects.filter(
        #     exposure_start_date__lte = today,
        #     exposure_end_date__gte = today,    
        # ).order_by("-id")

        articles = ArticleModel.objects.all()

        return Response(serializer, status=status.HTTP_200_OK)
    
    def post(self, request):
        file = request.data.get("image")
        number = request.data.get("number", "6")
        # print(file)
        # print(number)
        # if len(content) <= 5:
        #     return Response({"error": "내용은 5자 이상 작성해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 이미지 업로드를 위한 임시 폴더 생성 : style_transfer/input
        default_storage.save('./input/input_img.jpg', ContentFile(file.read()))
        
        # 선택 모델의 목록 1 ~ 9
        model = ['style_transfer/models/composition_vii.t7',
                 'style_transfer/models/la_muse.t7',
                 'style_transfer/models/starry_night.t7',
                 'style_transfer/models/the_wave.t7',
                 'style_transfer/models/candy.t7',
                 'style_transfer/models/feathers.t7',
                 'style_transfer/models/mosaic.t7',
                 'style_transfer/models/the_scream.t7',
                 'style_transfer/models/udnie.t7'
                 ]

        model_number = model[int(number)]
        print(model[int(number)])

        style_transfer(model_number)

        shutil.rmtree('./style_transfer/input/')

        list_of_files = glob.glob('./style_transfer/output/*')  # * means all if need specific format then *.csv
        print(list_of_files)
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)

        # result_img = glob.glob('/*')
        # file_path = "Desktop/folder/myfile.txt"
        result_img = os.path.basename(latest_file)
        print(result_img)

        request.data['user'] = request.user.id
        ArticleImageModel.objects.post('image_url' ,result_img)
        # request.data['url'] = result_img
        # print(request.data)
        # serializer 에 url 필드 추가
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"글 작성 완료"})
        else:
            os.remove(latest_file)
            print(serializer.errors)
            return Response({"message":f'${serializer.errors}'}, 400)

# class ArticleView(APIView):

#     def get(self, request):
#         user = request.user.id
#         articles = Article.objects.filter(user_id=user)
#         articles = ArticleSerializer(articles, many=True).data

#         return Response(articles, status=status.HTTP_200_OK)
    
    
#     def post(self, request):
#         content = request.data.get("content", "")
#         file = request.data.get("file")
#         # 사용자가 선택한 모델의 넘버
#         number = request.data.get("number", "")

#         # 이미지 업로드를 위한 임시 폴더 생성 : style_transfer/input
#         default_storage.save('style_transfer/input/input_img.jpg', ContentFile(file.read()))

#         # 선택 모델의 목록 1 ~ 9
#         model = ['style_transfer/models/composition_vii.t7',
#                  'style_transfer/models/la_muse.t7',
#                  'style_transfer/models/starry_night.t7',
#                  'style_transfer/models/the_wave.t7',
#                  'style_transfer/models/candy.t7',
#                  'style_transfer/models/feathers.t7',
#                  'style_transfer/models/mosaic.t7',
#                  'style_transfer/models/the_scream.t7',
#                  'style_transfer/models/udnie.t7'
#                  ]

#         model_number = model[int(number)]
#         style_transfer(model_number)

#         shutil.rmtree('style_transfer/input/')

#         list_of_files = glob.glob('style_transfer/output/*')  # * means all if need specific format then *.csv
#         latest_file = max(list_of_files, key=os.path.getctime)


#         user = request.user.id
#         article = {'user': user, 'content': content, 'result_img': {file}}
#         # article = {'user': user, 'title': title, 'img_url': latest_file}
#         article_serializer = ArticleSerializer(data=article)
#         if article_serializer.is_valid():
#             article_serializer.save()
#             return Response(status=status.HTTP_200_OK)

#         else:
#             os.remove(latest_file)
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# '''
# 수정 및 삭제 로직 : 출처 내배캠 2기 5조

#     def put(self, request, article_id):
#         try:
#             article = Article.objects.get(id=article_id)
#         except Article.DoesNotExist:
#             return Response({"error": "존재하지 않는 게시물입니다."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         # article_serializer = ArticleSerializer(article, data=request.data, partial=True)
#         # article_serializer.is_valid(raise_exception=True)
#         # article_serializer.save()

#         return Response({"message": "put method"}, status=status.HTTP_200_OK)

#     def delete(self, request, article_id):
#         user = request.user.id
#         article = Article.objects.filter(id=article_id)
#         print(user)
#         print(article[0].user_id)
#         if user == article[0].user_id:
#             article.delete()
#             os.remove(article[0].img_url)
#             return Response({"message": "게시물이 삭제되었습니다."}, status=status.HTTP_200_OK)

#         return Response({"message": "실패."}, status=status.HTTP_400_BAD_REQUEST)
# '''



# '''
# 마이페이지 포스팅 조회
# '''

# class ArticleMyGalleryView(APIView):

#     def get(self, request):
#         user = request.user.id
#         articles = Article.objects.filter(user_id=user)
#         articles = ArticleSerializer(articles, many=True).data

#         return Response(articles, status=status.HTTP_200_OK)

#     def delete(self, request, article_id):
#         user = request.user.id
#         article = Article.objects.filter(id=article_id)
#         print(user)
#         print(article[0].user_id)
#         if user == article[0].user_id:
#             article.delete()
#             os.remove(article[0].img_url)
#             return Response({"message": "게시물이 삭제되었습니다."}, status=status.HTTP_200_OK)

#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
