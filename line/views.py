import os
import uuid
import logging
from datetime import date, datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.core.files import File
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import FollowEvent, PostbackEvent, MessageEvent, ImageMessage, ImageSendMessage, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, ConfirmTemplate,  CarouselTemplate,  CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn,  PostbackTemplateAction, DatetimePickerTemplateAction
from main import models

# Create your views here.

POSTAGE = 0

THANKS_FOR_FOLLOWING = 'いつもご利用ありがとうございます！\n'\
+ 'enyfarは、スーツケースを格安でレンタルすることができるサービスです\n'\
+ 'お支払い以外の手続きを、すべてこのLINEトークルームで完結させることができます\n\n'\
+ '下のボタンから、したい操作を選んでください'

THANKS_FOR_USING = 'いつもご利用ありがとうございます！\n'\
+ 'enyfarは、スーツケースを格安でレンタルすることができるサービスです\n'\
+ 'お支払い以外の手続きを、すべてこのLINEトークルームで完結させることができます\n\n'\
+ '下のボタンから、したい操作を選んでください'

SELECT_START_DATE = 'レンタル開始日を選択してください'

SELECT_RETURN_DATE = '返却日を選択してください'

INPUT_ZIP_CODE = '郵便番号を入力してください\n'\
+ '（半角数字7桁・ハイフンなし）\n\n'\
+ '（例）1500043'

INPUT_ADDRESS = '住所を入力してください\n\n'\
+ '(例)東京都渋谷区道玄坂2-10-12 新大宗ビル3号館531'

INPUT_NAME = 'お名前（宛名）を入力してください\n\n'\
+ '(例)松澤 直輝'

INPUT_PHONE_NUMBER = '電話番号を入力してください\n'\
+ '（半角数字・ハイフンなし）\n\n'\
+ '（例）0312345678'

ABOUT_PAYMENT = 'お支払い方法と期限については、レンタル日前までにご連絡いたしますので、ご対応をお願い致します'



@csrf_exempt
def callback(request):
    if request.method == 'POST':
        line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
        logger = logging.getLogger(__name__)

        body = request.body.decode('utf-8')
        signature = request.META['HTTP_X_LINE_SIGNATURE']

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:

            meta_models = [models.Size, models.Type, models.ColorCategory, models.Bland]
            meta_data = [
                [
                    models.Size(
                        name='S',
                        data='S',
                        description='～40L',
                        min_days=1,
                        max_days=3
                    ),
                    models.Size(
                        name='M',
                        data='M',
                        description='41L～70L',
                        min_days=3,
                        max_days=5
                    ),
                    models.Size(
                        name='L',
                        data='L',
                        description='71L～90L',
                        min_days=5,
                        max_days=10
                    ),
                    models.Size(
                        name='LL',
                        data='LL',
                        description='91L～',
                        min_days=10
                    ),
                ],
                [
                    models.Type(
                        name='フレームタイプ',
                        data='frame',
                        description='丈夫で安全',
                        image='img/type/frame.jpg'
                    ),
                    models.Type(
                        name='ファスナータイプ',
                        data='fastener',
                        description='手ごろなお値段',
                        image='img/type/fastener.jpg'
                    ),
                ],
                [
                    models.ColorCategory(
                        name='ブラック',
                        data='black',
                        code='#333333'
                    ),
                    models.ColorCategory(
                        name='ブルー',
                        data='blue',
                        code='#000080'
                    ),
                    models.ColorCategory(
                        name='ホワイト',
                        data='white',
                        code='#FFFFFF'
                    ),
                    models.ColorCategory(
                        name='シルバー',
                        data='silver',
                        code='#000080'
                    ),
                ],
                [
                    models.Bland(
                        name='Rimowa(リモワ)',
                        data='rimowa'
                    ),
                    models.Bland(
                        name='Samsonite(サムソナイト)',
                        data='samsonite'
                    )
                ]
            ]

            for Model, data in zip(meta_models, meta_data):
                try:
                    object = Model.objects.all()[0]
                except IndexError:
                    Model.objects.bulk_create(data)

            items = [
                models.Item(
                    name='RIMOWA CLASSIC FLIGHT 35L',
                    data='rimowa-classic_silver_35',
                    description='リモワ RIMOWA クラシックフライト CLASSIC FLIGHT キャビンマルチホイール 35L シルバー スーツケース',
                    bland=models.Bland.objects.get(data='rimowa'),
                    size=models.Size.objects.get(data='S'),
                    type=models.Type.objects.get(data='frame'),
                    color_category=models.ColorCategory.objects.get(data='silver'),
                    color='シルバー',
                    capacity=35,
                    is_tsa=True,
                    fee_intercept=5000
                ),
                models.Item(
                    name='Samsonite Cosmolite Spinner',
                    data='samsonite-cosmolite_silver_36',
                    description='サムソナイト スーツケース SAMSONITE 73351 25 シルバー',
                    bland=models.Bland.objects.get(data='samsonite'),
                    size=models.Size.objects.get(data='S'),
                    type=models.Type.objects.get(data='fastener'),
                    color_category=models.ColorCategory.objects.get(data='silver'),
                    color='シルバー',
                    capacity=36,
                    is_tsa=True,
                    fee_intercept=2500
                )
            ]
            try:
                object = models.Item.objects.all()[0]
            except IndexError:
                models.Item.objects.bulk_create(items)

            item_models = [models.ItemImage, models.ItemFeeCoef]
            item_data = [
                [
                    models.ItemImage(
                        item = models.Item.objects.get(data='rimowa-classic_silver_35'),
                        image='img/item/rimowa-classic_silver_35.jpg',
                        order=1
                    ),
                    models.ItemImage(
                        item = models.Item.objects.get(data='samsonite-cosmolite_silver_36'),
                        image='img/item/samsonite-cosmolite_silver_36.jpg',
                        order=1
                    )
                ],
                [
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='rimowa-classic_silver_35'),
                        fee_coef=500,
                        starting_point=0,
                        end_point=3
                    ),
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='rimowa-classic_silver_35'),
                        fee_coef=400,
                        starting_point=3,
                        end_point=5
                    ),
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='rimowa-classic_silver_35'),
                        fee_coef=300,
                        starting_point=5
                    ),
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='samsonite-cosmolite_silver_36'),
                        fee_coef=400,
                        starting_point=0,
                        end_point=3
                    ),
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='samsonite-cosmolite_silver_36'),
                        fee_coef=300,
                        starting_point=3,
                        end_point=5
                    ),
                    models.ItemFeeCoef(
                        item = models.Item.objects.get(data='samsonite-cosmolite_silver_36'),
                        fee_coef=200,
                        starting_point=0,
                        end_point=5
                    )
                ]
            ]

            for Model, data in zip(item_models, item_data):
                try:
                    object = Model.objects.all()[0]
                except IndexError:
                    Model.objects.bulk_create(data)



            line_id = event.source.user_id
            line_user, _ = models.LINEUser.objects.get_or_create(line_id=line_id)
            all_reservations = models.Reservation.objects.order_by('-created_at')
            reservations = all_reservations.filter(line_user=line_user).order_by('-created_at')

            line_ids = []
            for reservation in all_reservations:
                line_ids.append(reservation.line_user.line_id)

            has_created = line_id in line_ids
            if has_created == True:
                reservation = models.Reservation.objects.filter(line_user=line_user).order_by('-created_at')[0]



            ## utils ##

            def _item_date_checker():
                text = '条件に一致する商品はこちらになります\n'\
                + '詳細を見たい商品の「詳細を見る」タップしてください'
                items = models.Item.objects.filter(size=reservation.size, type=reservation.type)

                for item in items:
                    for r in item.reservation_set.all():
                        if r.uuid != reservation.uuid and not (r.return_date + timedelta(days=1) < reservation.start_date or reservation.return_date < r.start_date - timedelta(days=1)):
                            items = items.exclude(data=r.item.data)

                if not len(items):
                    text = '条件に一致する商品が見つからなかったため、条件の類似した商品を表示しています\n'\
                    + '詳細を見たい商品の「詳細を見る」タップしてください'
                    items = models.Item.objects.filter(Q(size=reservation.size) or Q(type=reservation.type))

                    for item in items:
                        for r in item.reservation_set.all():
                                if r.uuid != reservation.uuid and not (r.return_date + timedelta(days=1) < reservation.start_date or reservation.return_date < r.start_date - timedelta(days=1)):
                                    items = items.exclude(data=r.item.data)

                return items, text

            def _fee_calculator(item):
                intercept = item.fee_intercept
                coefs = item.item_fee_coef_set.order_by('starting_point')
                fee = intercept

                delta = reservation.return_date - reservation.start_date
                days = delta.days + 1

                for coef in coefs:
                    fee_coef = coef.fee_coef
                    starting_point = coef.starting_point
                    end_point = coef.end_point

                    if end_point:
                        if days <= end_point:
                            fee += fee_coef * (days - starting_point)
                            return fee
                        elif end_point < days:
                            fee += fee_coef * (end_point - starting_point)
                    else:
                        fee += fee_coef * (days - starting_point)
                        return fee

                return fee



            ## prompter ##

            def _text_message(arg):
                reply = line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(arg)
                )
                return reply

            def _date_prompter(text1, text2, data, min, max):
                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text1),
                        TemplateSendMessage(
                            alt_text=text1,
                            template=ButtonsTemplate(
                                title='選択',
                                text=text2,
                                actions=[
                                    DatetimePickerTemplateAction(
                                        label='選択',
                                        data=data,
                                        mode='date',
                                        initial=min,
                                        min=min,
                                        max=max
                                    )
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _start_date_prompter():
                reply = _date_prompter(SELECT_START_DATE, SELECT_START_DATE, 'start_date', '2018-08-01', '2019-08-01')
                return reply

            def _return_date_prompter(check=None):
                start_date_check = '開始日は {}年{}月{}日 ですね\n\n次は、'.format(reservation.start_date.year, reservation.start_date.month, reservation.start_date.day)
                text1 = text2 = SELECT_RETURN_DATE
                if check:
                    text1 = start_date_check + text1

                min = reservation.start_date + timedelta(days=1)
                max = reservation.start_date + timedelta(days=365)
                reply = _date_prompter(text1, text2, 'return_date', min.strftime('%Y-%m-%d'), max.strftime('%Y-%m-%d'))
                return reply

            def _size_prompter(check=None):

                delta = reservation.return_date - reservation.start_date
                days = delta.days + 1

                sizes = models.Size.objects.order_by('min_days')
                actions = [ PostbackTemplateAction(label='{} ({})'.format(size.name, size.description), data=size.data) for size in sizes ]

                for size in sizes:
                    min = size.min_days
                    max = size.max_days
                    if min and max:
                        if min <= days < max:
                            recommendation = size.name
                    elif min and not max:
                        if min <= days:
                            recommendation = size.name

                return_date_check = '返却日は {}年{}月{}日 ですね\n\n次は、'.format(reservation.return_date.year, reservation.return_date.month, reservation.return_date.day)
                text = 'サイズを選択してください\n{}日間のレンタルなら、{}サイズがおすすめです'.format(days, recommendation)
                if check:
                    text = return_date_check + text

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='サイズを選択',
                            template=ButtonsTemplate(
                                title='サイズを選択',
                                text='{}日間のレンタルなら、{}サイズがおすすめです'.format(days, recommendation),
                                actions=actions
                            )
                        )
                    ]
                )
                return reply

            def _type_prompter(check=None):
                size_check = '{}サイズですね\n\n次は、'.format(reservation.size)
                text = 'スーツケースの鍵・明け口のタイプを選択してください'
                if check:
                    text = size_check + text

                types = models.Type.objects.all()

                columns = []
                for type in types:
                    columns.append(
                        CarouselColumn(
                            thumbnail_image_url='https://enyfar.net{}'.format(type.image.url),
                            title=type.name,
                            text=type.description,
                            actions=[
                                PostbackTemplateAction(
                                    label='このタイプにする',
                                    data=type.data
                                )
                            ]
                        )
                    )

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='タイプを選択',
                            template=CarouselTemplate(
                                columns=columns
                            )
                        )
                    ]
                )
                return reply


                # actions = [ PostbackTemplateAction(label=type.name, data=type.data) for type in types ]
                #
                # reply = line_bot_api.reply_message(
                #     event.reply_token,
                #     [
                #         TextSendMessage(),
                #         TemplateSendMessage(
                #             alt_text='タイプを選択',
                #             template=ButtonsTemplate(
                #                 title='タイプを選択',
                #                 text='選択してください',
                #                 actions=actions
                #             )
                #         )
                #     ]
                # )
                # return reply

            def _item_select_prompter():
                items, text1 = _item_date_checker()

                columns = []
                for item in items:
                    text2 = '価格：￥{}～\n'.format(item.fee_intercept + item.item_fee_coef_set.order_by('starting_point')[0].fee_coef * 2)\
                    + 'ブランド：{}\n'.format(item.bland)\
                    + 'カラー：{}'.format(item.color)
                    image = item.item_image_set.order_by('order')[0].image.url
                    columns.append(
                        CarouselColumn(
                            thumbnail_image_url='https://enyfar.net{}'.format(image),
                            title=item.name,
                            text=text2,
                            actions=[
                                PostbackTemplateAction(
                                     label='詳細を見る',
                                     data=str(item.data)
                                 )
                            ]
                        )
                    )

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text1),
                        TemplateSendMessage(
                            alt_text='商品リスト',
                            template=CarouselTemplate(
                                image_aspect_ratio='square',
                                columns=columns
                            )
                        )
                    ]
                )
                return reply

            def _item_decision_prompter(arg):
                item = models.Item.objects.get(data=arg)

                text1 = '商品の詳細です\n'\
                + 'こちらの商品でよろしいですか？'
                text2 = '【商品詳細】\n\n'\
                + '商品名：{}\n'.format(item.name)\
                + 'ブランド{}\n'.format(item.bland)\
                + '容量：{}L ({})\n'.format(item.capacity, item.size)\
                + 'タイプ：{}\n'.format(item.type)\
                + 'カラー：{}\n'.format(item.color)\
                + '料金（送料を含む）：￥{}'.format(_fee_calculator(item))
                item_images = item.item_image_set.order_by('order')

                columns = []
                for item_image in item_images:
                    columns.append(
                        ImageCarouselColumn(
                            image_url='https://enyfar.net{}'.format(item_image.image.url),
                            action=PostbackTemplateAction(
                                 label='画像{}'.format(str(item_image.order)),
                                 data='_'
                             )
                        )
                    )

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text1),
                        TemplateSendMessage(
                            alt_text='商品画像',
                            template=ImageCarouselTemplate(
                                columns=columns
                            )
                        ),
                        TextSendMessage(text2),
                        TemplateSendMessage(
                            alt_text='確認',
                            template=ConfirmTemplate(
                                text='こちらの商品でよろしいですか？',
                                actions=[
                                    PostbackTemplateAction(
                                        label='はい',
                                        data=item.data
                                    ),
                                    PostbackTemplateAction(
                                        label='いいえ',
                                        data='not_choose'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _registration_prompter():
                text = '次のお届け先が保存されています\n'\
                + 'このお届け先を使用しますか？\n\n'\
                + '【お届け先情報】\n'\
                + '〒{}\n'.format(line_user.zip_code)\
                + '{}\n'.format(line_user.address)\
                + 'お名前：{}\n'.format(line_user.name)
                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='確認',
                            template=ConfirmTemplate(
                                text='保存されているお届け先を使用しますか？',
                                actions=[
                                    PostbackTemplateAction(
                                        label='はい',
                                        data='use_default'
                                    ),
                                    PostbackTemplateAction(
                                        label='いいえ',
                                        data='not_use_default'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _check_prompter():
                text = '項目の入力が完了しました\n'\
                + '予約内容は以下の通りです\n\n'\
                + '【予約内容】\n'\
                + '開始日：{}年{}月{}日\n'.format(reservation.start_date.year, reservation.start_date.month, reservation.start_date.day)\
                + '返却日：{}年{}月{}日\n'.format(reservation.return_date.year, reservation.return_date.month, reservation.return_date.day)\
                + '住所：〒{} {}\n'.format(reservation.zip_code, reservation.address)\
                + 'お名前：{}\n\n'.format(reservation.name)\
                + '【料金】\n'\
                + '小計：￥{}\n'.format(reservation.item_fee)\
                + '送料：￥{}\n'.format(reservation.postage)\
                + 'ご請求額：￥{}\n\n'.format(reservation.total_fee)\
                + '【商品詳細】\n'\
                + '商品名：{}\n'.format(reservation.item.name)\
                + 'ブランド{}\n'.format(reservation.item.bland)\
                + '容量：{}L ({})\n'.format(reservation.item.capacity, reservation.item.size)\
                + 'タイプ：{}\n'.format(reservation.item.type)\
                + 'カラー：{}\n\n'.format(reservation.item.color)\
                + 'この内容で予約を確定する場合は「確定」、予約内容を修正する場合は「修正」、予約を中止する場合は「中止」を押してください'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='確認',
                            template=ButtonsTemplate(
                                title='確認',
                                text='予約内容を確認し、操作を選んでください',
                                actions=[
                                    PostbackTemplateAction(
                                        label='確定',
                                        data='confirm'
                                    ),
                                    PostbackTemplateAction(
                                        label='修正',
                                        data='modify'
                                    ),
                                    PostbackTemplateAction(
                                        label='中止',
                                        data='quit'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _register_prompter():
                text = '予約が確定しました\n'\
                + '今回のお届け先を次回以降も利用できるように保存しますか？\n\n'\
                + '【お届け先】\n'\
                + '〒{}\n'.format(reservation.zip_code)\
                + '{}\n'.format(reservation.address)\
                + 'お名前：{}'.format(reservation.name)

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='確認',
                            template=ConfirmTemplate(
                                text='次回以降、このお届け先を利用できるように保存しますか？',
                                actions=[
                                    PostbackTemplateAction(
                                        label='はい',
                                        data='register'
                                    ),
                                    PostbackTemplateAction(
                                        label='いいえ',
                                        data='not_register'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _modification_prompter():
                text = 'どの項目を修正しますか？\n\n'\
                + '・レンタルする日にちを変更したい場合は「レンタル期間」\n'\
                + '・住所・お名前・電話番号を変更したい場合は「お届け先情報」\n'\
                + '・商品を変更したい場合は「商品」\n\n'\
                + 'をタップするか、入力してください'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='修正',
                            template=ButtonsTemplate(
                                title='修正',
                                text='修正したい項目をタップしてください',
                                actions=[
                                    PostbackTemplateAction(
                                        label='レンタル期間',
                                        data='modify_rental_period'
                                    ),
                                    PostbackTemplateAction(
                                        label='商品',
                                        data='modify_item'
                                    ),
                                    PostbackTemplateAction(
                                        label='お届け先情報',
                                        data='modify_destination'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _item_modification_prompter():
                text = 'アイテムを探す方法を選択してください'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='アイテムを探す',
                            template=ButtonsTemplate(
                                title='アイテムを探す',
                                text='方法を選択してください',
                                actions=[
                                    PostbackTemplateAction(
                                        label='類似商品を表示する',
                                        data='list_item'
                                    ),
                                    PostbackTemplateAction(
                                        label='条件を変更する',
                                        data='modify_condition'
                                    )
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _item_condition_modification_prompter():
                reservation.item = None
                reservation.save()
                text = 'どの項目を修正しますか？\n\n'\
                + '修正したい項目ををタップするか、入力してください'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='修正',
                            template=ButtonsTemplate(
                                title='修正',
                                text='修正したい項目をタップしてください',
                                actions=[
                                    PostbackTemplateAction(
                                        label='サイズ：{}'.format(reservation.size),
                                        data='modify_size'
                                    ),
                                    PostbackTemplateAction(
                                        label='タイプ：{}'.format(reservation.type),
                                        data='modify_type'
                                    )
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _destination_modification_prompter():
                text = 'どの項目を修正しますか？\n\n'\
                + '修正したい項目ををタップするか、入力してください'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='修正',
                            template=ButtonsTemplate(
                                title='修正',
                                text='修正したい項目をタップしてください',
                                actions=[
                                    PostbackTemplateAction(
                                        label='郵便番号・住所',
                                        data='modify_address'
                                    ),
                                    PostbackTemplateAction(
                                        label='お名前',
                                        data='modify_name'
                                    )
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _delete_prompter():
                text = '予約を中止しますか？\n'\
                + '入力した内容は完全に削除されます\n\n'\
                + '※この操作は取り消せません\n'\

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='予約を中止',
                            template=ConfirmTemplate(
                                text='予約を中止しますか？この操作は取り消せません。',
                                actions=[
                                    PostbackTemplateAction(
                                        label='はい',
                                        data='delete'
                                    ),
                                    PostbackTemplateAction(
                                        label='いいえ',
                                        data='not_delete'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _reconfirmation_prompter():
                text1 = '現在、予約済みの商品は' + str(line_ids.count(line_id)) + '個あります\n'\
                + '詳細を見たい予約をタップしてください'
                columns = []

                for reservation in reservations:
                    start_date = reservation.start_date
                    return_date = reservation.return_date
                    title = '{}/{}/{} ～ {}/{}/{}'.format(start_date.year, start_date.month, start_date.day, return_date.year, return_date.month, return_date.day)
                    text2 = '〒{} {}'.format(reservation.zip_code, reservation.address)
                    image = reservation.item.item_image_set.order_by('order')[0].image.url

                    columns.append(
                        CarouselColumn(
                            thumbnail_image_url='https://enyfar.net{}'.format(image),
                            title=title,
                            text=text2,
                            actions=[
                                PostbackTemplateAction(
                                     label='詳細を見る',
                                     data=str(reservation.uuid)
                                 )
                            ]
                        )
                    )

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text1),
                        TemplateSendMessage(
                            alt_text='予約リスト',
                            template=CarouselTemplate(
                                image_aspect_ratio='square',
                                columns=columns
                            )
                        )
                    ]
                )
                return reply

            def _remodification_prompter():
                reservation_selected = reservations.get(uuid=event.postback.data)
                text1 = '予約内容は以下の通りです\n\n'\
                + '【予約内容】\n'\
                + '開始日：{}年{}月{}日\n'.format(reservation_selected.start_date.year, reservation_selected.start_date.month, reservation_selected.start_date.day)\
                + '返却日：{}年{}月{}日\n'.format(reservation_selected.return_date.year, reservation_selected.return_date.month, reservation_selected.return_date.day)\
                + 'お届け先住所：〒{} {}\n'.format(reservation_selected.zip_code, reservation_selected.address)\
                + 'お名前：{}\n'.format(reservation_selected.name)\
                + '【料金】\n'\
                + '小計：￥{}\n'.format(reservation_selected.item_fee)\
                + '送料：￥{}\n\n'.format(reservation_selected.postage)\
                + '合計料金：￥{}\n\n'.format(reservation_selected.total_fee)\
                + '【商品詳細】\n'\
                + '商品名：{}\n'.format(reservation_selected.item.name)\
                + 'ブランド{}\n'.format(reservation_selected.item.bland)\
                + '容量：{}L ({})\n'.format(reservation_selected.item.capacity, reservation_selected.item.size)\
                + 'タイプ：{}\n'.format(reservation_selected.item.type)\
                + 'カラー：{}'.format(reservation_selected.item.color)
                text2 = '予約を変更、または取り消したい場合には、以下のメールアドレスまでご連絡ください\n\n'\
                + 'メール：info@anybirth.co.jp'

                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text1),
                        TextSendMessage(text2)
                    ]
                )
                return reply



            ## reciever ##

            def _thanks(text):
                reply = line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text),
                        TemplateSendMessage(
                            alt_text='操作',
                            template=ButtonsTemplate(
                                title='操作',
                                text='下のボタンを押すと次へ進みます',
                                actions=[
                                    PostbackTemplateAction(
                                        label='新規予約',
                                        data='reservation'
                                    ),
                                    PostbackTemplateAction(
                                        label='予約履歴',
                                        data='reconfirmation'
                                    ),
                                ]
                            )
                        )
                    ]
                )
                return reply

            def _thanks_for_following():
                _thanks(THANKS_FOR_FOLLOWING)

            def _thanks_for_using():
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        if event.message.text in ['予約', '予約する', '予約したい', '新規予約', '新規予約する', '新規予約したい', 'よやく', 'しんきよやく']:
                            reservation = models.Reservation(line_user=line_user, status=1)
                            reservation.save()
                            _start_date_prompter()
                        elif event.message.text in ['予約履歴', '履歴']:
                            if line_ids.count(line_id):
                                _reconfirmation_prompter()
                            else:
                                _text_message('予約されている商品はありません')
                        else:
                            _thanks(THANKS_FOR_USING)
                elif isinstance(event, PostbackEvent):
                    if event.postback.data == 'reservation':
                        reservation = models.Reservation(line_user=line_user, status=1)
                        reservation.save()
                        _start_date_prompter()
                    elif event.postback.data == 'reconfirmation':
                        if line_ids.count(line_id):
                            _reconfirmation_prompter()
                        else:
                            _text_message('予約されている商品はありません')
                    elif uuid.UUID(event.postback.data) in reservations.values_list('uuid', flat=True):
                        reservation_selected = reservations.get(uuid=event.postback.data)
                        _remodification_prompter()

            def _start_date_reciever(next_status, func, check=None, **kwargs):
                if isinstance(event, PostbackEvent):
                    if event.postback.data == 'start_date':
                        reservation.start_date = datetime.strptime(event.postback.params['date'], '%Y-%m-%d').date()
                        reservation.status = next_status
                        reservation.save()
                        if check:
                            try:
                                func(check=check)
                            except TypeError:
                                func(arg=kwargs['arg'], check=check)
                        else:
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])

            def _return_date_reciever(next_status, func, check=None, **kwargs):
                if isinstance(event, PostbackEvent):
                    if event.postback.data == 'return_date':
                        reservation.return_date = datetime.strptime(event.postback.params['date'], '%Y-%m-%d').date()
                        reservation.status = next_status
                        reservation.save()
                        if reservation.item:
                            reservation.item_fee = _fee_calculator(item=reservation.item)
                            reservation.postage = POSTAGE
                            reservation.total_fee = reservation.item_fee + reservation.postage
                            reservation.save()
                        if check:
                            try:
                                func(check=check)
                            except TypeError:
                                func(arg=kwargs['arg'], check=check)
                        else:
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])


            def _size_reciever(next_status, func, check=None, **kwargs):
                if isinstance(event, PostbackEvent):
                    data = models.Size.objects.all().values_list('data', flat=True)
                    if event.postback.data in data:
                        reservation.size = models.Size.objects.get(data=event.postback.data)
                        reservation.status = next_status
                        reservation.save()
                        if check:
                            try:
                                func(check=check)
                            except TypeError:
                                func(arg=kwargs['arg'], check=check)
                        else:
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])

                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        names = models.Size.objects.all().values_list('name', flat=True)
                        if event.message.text in names:
                            reservation.size = models.Size.objects.get(name=event.message.text)
                            reservation.status = next_status
                            reservation.save()
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])

            def _type_reciever(next_status, func, **kwargs):
                if isinstance(event, PostbackEvent):
                    data = models.Type.objects.all().values_list('data', flat=True)
                    if event.postback.data in data:
                        reservation.type = models.Type.objects.get(data=event.postback.data)
                        reservation.status = next_status
                        reservation.save()
                        try:
                            func()
                        except TypeError:
                            func(arg=kwargs['arg'])

                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        names = models.Type.objects.all().values_list('name', flat=True)
                        if event.message.text in names:
                            reservation.type = models.Type.objects.get(name=event.message.text)
                            reservation.status = next_status
                            reservation.save()
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])

            def _item_select_reciever(next_status, func, **kwargs):
                if isinstance(event, PostbackEvent):
                    data = models.Item.objects.all().values_list('data', flat=True)
                    if event.postback.data in data:
                        reservation.status = next_status
                        reservation.save()
                        try:
                            func()
                        except TypeError:
                            func(arg=kwargs['arg'])

            def _item_decision_reciever(next_status, func, prompt_default=False, **kwargs):
                if isinstance(event, PostbackEvent):
                    data = models.Item.objects.all().values_list('data', flat=True)
                    if event.postback.data in data:
                        reservation.item = models.Item.objects.get(data=event.postback.data)
                        reservation.size = reservation.item.size
                        reservation.type = reservation.item.type
                        reservation.item_fee = _fee_calculator(item=reservation.item)
                        reservation.postage = POSTAGE
                        reservation.total_fee = reservation.item_fee + reservation.postage
                        if prompt_default and line_user.zip_code and line_user.address and line_user.name:
                            reservation.status = 11
                            reservation.save()
                            _registration_prompter()
                        else:
                            reservation.status = next_status[0]
                            reservation.save()
                            try:
                                func[0]()
                            except TypeError:
                                func[0](kwargs['arg'][0])
                    elif event.postback.data == 'not_choose':
                        reservation.status = next_status[1]
                        reservation.save()
                        try:
                            func[1]()
                        except TypeError:
                            func[1](kwargs['arg'][1])

                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        names = models.Item.objects.all().values_list('data', flat=True)
                        if event.message.text in names or event.postback.data == 'はい':
                            reservation.item = models.Item.objects.get(name=event.message.text)
                            reservation.size = reservation.item.size
                            reservation.type = reservation.item.type
                            reservation.item_fee = _fee_calculator(reservation.item)
                            reservation.postage = POSTAGE
                            reservation.total_fee = reservation.item_fee + reservation.postage
                            if prompt_default and line_user.zip_code and line_user.address and line_user.name:
                                reservation.status = 11
                                reservation.save()
                                _registration_prompter()
                            else:
                                reservation.status = next_status[0]
                                reservation.save()
                                try:
                                    func[0]()
                                except TypeError:
                                    func[0](kwargs['arg'][0])
                        elif event.message.text == 'いいえ':
                            reservation.status = next_status2
                            reservation.save()
                            try:
                                func[1]()
                            except TypeError:
                                func[1](kwargs['arg'][1])

            def _zip_code_reciever(next_status, func, **kwargs):
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        text = event.message.text
                        if len(text) == 7 and text.isdecimal() and text.encode('utf-8').isalnum():
                            reservation.zip_code = text
                            reservation.status = next_status
                            reservation.save()
                            line_user.save()
                            try:
                                func()
                            except TypeError:
                                func(arg=kwargs['arg'])
                        elif len(text) == 7 and text.isdecimal() and not text.encode('utf-8').isalnum():
                            _text_message('半角で入力してください')
                        elif len(text) == 8 and text.find('-') == 3:
                            _text_message('ハイフンなしで入力してください')
                        else:
                            _text_message('半角数字7桁・ハイフンなしで入力してください')

            def _address_reciever(next_status, func, **kwargs):
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        reservation.address = event.message.text
                        reservation.status = next_status
                        reservation.save()
                        line_user.save()
                        try:
                            func()
                        except TypeError:
                            func(arg=kwargs['arg'])

            def _name_reciever(next_status, func, **kwargs):
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        reservation.name = event.message.text
                        reservation.status = next_status
                        reservation.save()
                        line_user.save()
                        try:
                            func()
                        except TypeError:
                            func(arg=kwargs['arg'])

            def _using_default_reciever(**kwargs):
                if isinstance(event, PostbackEvent):
                    if event.postback.data == 'use_default':
                        reservation.zip_code = line_user.zip_code
                        reservation.address = line_user.address
                        reservation.name = line_user.name
                        reservation.status = 91
                        reservation.save()
                        _check_prompter()
                    elif event.postback.data == 'not_use_default':
                        reservation.status = 12
                        reservation.save()
                        _text_message(INPUT_ZIP_CODE)

            def _register_reciever():
                if isinstance(event, PostbackEvent):
                    if event.postback.data == 'register':
                        line_user.zip_code = reservation.zip_code
                        line_user.address = reservation.address
                        line_user.name = reservation.name
                        line_user.save()
                        reservation.status = 0
                        reservation.save()
                        _text_message('お届け先を保存しました\n\n' + ABOUT_PAYMENT)
                    elif event.postback.data == 'not_register':
                        if not line_user.name:
                            line_user.name = reservation.name
                            line_user.save()
                        reservation.status = 0
                        reservation.save()
                        _text_message('予約が全て完了しました\n' + ABOUT_PAYMENT)

            def _postback_reciever(data, next_status, func, **kwargs):
                if isinstance(event, PostbackEvent):
                    for i in range(0, len(data)):
                        if event.postback.data == data[i]:
                            reservation.status = next_status[i]
                            reservation.save()
                            try:
                                func[i]()
                            except TypeError:
                                func[i](arg=kwargs['arg'][i])

            def _delete_reciever():
                if isinstance(event, PostbackEvent):
                    if event.postback.data == 'delete':
                        reservation.delete()
                        _text_message('予約を削除しました')
                    elif event.postback.data == 'not_delete':
                        reservation.status = 91
                        reservation.save()
                        _check_prompter()



            ## main process ##

            if isinstance(event, FollowEvent):
                _thanks_for_following()

            if has_created == False:
                _thanks_for_using()

            elif has_created == True:
                if reservation.status == 0:
                    _thanks_for_using()

                elif reservation.status == 1:
                    _start_date_reciever(next_status=2, func=_return_date_prompter, check=True)

                elif reservation.status == 2:
                    _return_date_reciever(next_status=3, func=_size_prompter, check=True)

                elif reservation.status == 3:
                    _size_reciever(next_status=4, func=_type_prompter, check=True)

                elif reservation.status == 4:
                    _type_reciever(next_status=5, func=_item_select_prompter)

                elif reservation.status == 5:
                    _item_select_reciever(next_status=6, func=_item_decision_prompter, arg=event.postback.data)

                elif reservation.status == 6:
                    _item_decision_reciever(next_status=(7, 21), func=(_text_message, _item_modification_prompter), arg=(INPUT_ZIP_CODE, None), prompt_default=True)

                elif reservation.status == 7:
                    _zip_code_reciever(next_status=8, func=_text_message, arg=INPUT_ADDRESS)

                elif reservation.status == 8:
                    _address_reciever(next_status=9, func=_text_message, arg=INPUT_NAME)

                elif reservation.status == 9:
                    _name_reciever(next_status=91, func=_check_prompter)


                elif reservation.status == 11:
                    _using_default_reciever()

                elif reservation.status == 12:
                    _zip_code_reciever(next_status=8, func=_text_message, arg=INPUT_ADDRESS)


                elif reservation.status == 21:
                    _postback_reciever(next_status=(22, 25), func=(_item_condition_modification_prompter, _item_select_prompter), data=('modify_condition', 'list_item'))

                elif reservation.status == 22:
                    _postback_reciever(next_status=(23, 24), func=(_size_prompter, _type_prompter), data=('modify_size', 'modify_type'))

                elif reservation.status == 23:
                    _size_reciever(next_status=25, func=_item_select_prompter)

                elif reservation.status == 24:
                    _type_reciever(next_status=25, func=_item_select_prompter)

                elif reservation.status == 25:
                    _item_select_reciever(next_status=26, func=_item_decision_prompter, arg=event.postback.data)

                elif reservation.status == 26:
                    _item_decision_reciever(next_status=(7, 21), func=(_text_message, _item_modification_prompter), arg=(INPUT_ZIP_CODE, None), prompt_default=True)


                elif reservation.status == 31:
                    _start_date_reciever(next_status=32, func=_return_date_prompter, check=True)

                elif reservation.status == 32:
                    _return_date_reciever(next_status=43, func=_size_prompter, check=True)

                elif reservation.status == 33:
                    _size_reciever(next_status=35, func=_item_select_prompter)

                elif reservation.status == 34:
                    _type_reciever(next_status=35, func=_item_select_prompter)

                elif reservation.status == 35:
                    _item_select_reciever(next_status=36, func=_item_decision_prompter, arg=event.postback.data)

                elif reservation.status == 36:
                    _item_decision_reciever(next_status=(91, 94), func=(_check_prompter, _item_modification_prompter))

                elif reservation.status == 37:
                    _zip_code_reciever(next_status=38, func=_text_message, arg=INPUT_ADDRESS)

                elif reservation.status == 38:
                    _address_reciever(next_status=91, func=_check_prompter)

                elif reservation.status == 39:
                    _name_reciever(next_status=91, func=_check_prompter)


                elif reservation.status == 43:
                    _size_reciever(next_status=44, func=_type_prompter, check=True)

                elif reservation.status == 44:
                    _type_reciever(next_status=45, func=_item_select_prompter)

                elif reservation.status == 45:
                    _item_select_reciever(next_status=46, func=_item_decision_prompter, arg=event.postback.data)

                elif reservation.status == 46:
                    _item_decision_reciever(next_status=(91, 94), func=(_check_prompter, _item_modification_prompter))


                elif reservation.status == 91:
                    _postback_reciever(next_status=(92, 93, 99), func=(_register_prompter, _modification_prompter, _delete_prompter), data=('confirm', 'modify', 'quit'))

                elif reservation.status == 92:
                    _register_reciever()

                elif reservation.status == 93:
                    _postback_reciever( next_status=(31, 94, 96), func=(_start_date_prompter, _item_modification_prompter, _destination_modification_prompter), data=('modify_rental_period', 'modify_item', 'modify_destination'))

                elif reservation.status == 94:
                    _postback_reciever(next_status=(95, 35), func=(_item_condition_modification_prompter, _item_select_prompter), data=('modify_condition', 'list_item'))

                elif reservation.status == 95:
                    _postback_reciever(next_status=(33, 34), func=(_size_prompter, _type_prompter), data=('modify_size', 'modify_type'))

                elif reservation.status == 96:
                    _postback_reciever(next_status=(37, 39), func=(_text_message, _text_message), arg=(INPUT_ZIP_CODE, INPUT_NAME), data=('modify_address', 'modify_name'))

                elif reservation.status == 99:
                    _delete_reciever()

        return HttpResponse()
    else:
        return HttpResponseBadRequest('<h1 style="text-align:center;font-weight:400;">HTTP Error 400 – Bad Request</h1>')