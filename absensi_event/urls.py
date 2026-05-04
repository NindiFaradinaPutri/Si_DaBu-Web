"""
Definition of urls for nganggur.
"""

from datetime import datetime

from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

from complaint import ajaxs as complaint_ajaxs
from news import ajaxs as news_ajaxs
from portfolio import ajaxs as prf_ajaxs
from gallery import ajaxs as gal_ajaxs

from views import (auth_views, fe_views, news_views, banner_views, portfolio_views, gallery_views, profile_views, team_views, mobile_views, complaint_views, finance_views as finn,information_views as info)
from views.mobile import mobile_auth_views as mobile_auth, mobile_event_views as mobile_event
from authentication import ajaxs as auth_ajaxs
from finance import ajaxs as fin_ajaxs, prints as fin_prints
from information import ajaxs as info_ajaxs


urlpatterns = [
    path('error_400/', auth_views.handler400, name='error_400'),
    path('error_404/', auth_views.handler404, name='error_404'),
    path('error_403/', auth_views.handler403, name='error_403'),
    path('error_500/', auth_views.handler500, name='error_500'),
       
    #Home
    path('', fe_views.home, name='index'),
    path('home/', fe_views.home, name='home'),
    #path('', auth_views.login, name='index'),

    url(r'^password/reset/$', PasswordResetView.as_view(template_name='template/registrations/password_reset_form.html'), name='password_reset'),
    url(r'^password/reset/done/$', PasswordResetDoneView.as_view(template_name='template/registrations/password_reset_done.html'), name='password_reset_done'),
    url(
    r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
    PasswordResetConfirmView.as_view(template_name='template/registrations/password_reset_confirm.html'),
    name='password_reset_confirm'
        ),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    # PasswordResetConfirmView.as_view(template_name='template/registrations/password_reset_confirm.html'), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(template_name='template/registrations/password_reset_complete.html'), name='password_reset_complete'),

    #Authentication
    #Page
    path('admin/who-login/', auth_views.login, name='who_login'),
    path('admin/signup/', auth_views.admin_signup, name='admin_signup'),
    path('admin/activation/<uidb64>/<token>/', auth_views.activate, name='admin_activation'),
    path('admin/post/reg/', auth_views.admin_post_registration, name='admin_post_registration'),
    path('admin/password/change/', auth_views.admin_password_change, name='admin_password_change'),

    path('admin/profile/', auth_views.admin_profile, name='admin_profile'),
    path('admin/profile/update/', auth_views.admin_profile_update, name='admin_profile_update'),

    path('admin/list/', auth_views.admin_list, name='admin_list'),
    path('admin/delete/', auth_views.admin_delete, name='admin_delete'),

    path('logout/', LogoutView.as_view(next_page='/admin/who-login/'), name='logout'),

    #ADDRESS ACCESS
    url(r'^ajax/akses_provinsi/$', auth_ajaxs.akses_provinsi,name="akses_provinsi"),
    url(r'^ajax/akses_dati2/$', auth_ajaxs.akses_dati2,name="akses_dati2"),
    url(r'^ajax/akses_kecamatan/$', auth_ajaxs.akses_kecamatan,name="akses_kecamatan"),
    url(r'^ajax/akses_kelurahan/$', auth_ajaxs.akses_kelurahan,name="akses_kelurahan"),

    #Ajax
    url(r'^ajax/check_account_activation/$', auth_ajaxs.check_account_activation,name="check_account_activation"),

    #Banner

    path('event/list/', banner_views.event_list, name='event_list'),
    path('event/add/', banner_views.event_add, name='event_add'), 
    re_path(r'^event/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', banner_views.event_update, name='event_update'), 

    path('banner/list/', banner_views.banner_list, name='banner_list'),
    path('banner/add/', banner_views.banner_add, name='banner_add'),  
    re_path(r'^banner/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', banner_views.banner_update, name='banner_update'),

    #About
    path('event/', fe_views.event_frontend, name='event'),
    path('profile/', profile_views.profile, name='profile'),

    #Portfolio
    path('portfolios/', portfolio_views.portfolio, name='portfolio'),
    url(r'^ajax/filter_portfolio/$', prf_ajaxs.filter_portfolio,name='filter_portfolio'),
    path('portfolios/list/', portfolio_views.portfolio_list, name='portfolio_list'),
    path('portfolios/add/', portfolio_views.portfolio_add, name='portfolio_add'),
    re_path(r'^portfolios/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', portfolio_views.portfolio_update, name='portfolio_update'),
    re_path(r'^portfolios/(?P<id>[0-9a-zA-Z-_]+)/$', portfolio_views.portfolio_service, name='portfolio_service'),
    url(r'^ajax/addform_portfoliophoto/$', prf_ajaxs.addform_portfoliophoto,name="addform_portfoliophoto"),
    url(r'^ajax/view_portfolio/$', prf_ajaxs.view_portfolio,name="view_portfolio"),
    url(r'^ajax/ctrg_portfolio/$', prf_ajaxs.ctrg_portfolio,name="ctrg_portfolio"),

    #News
    path('news/', news_views.news, name='news'),
    path('news/search', news_views.news_search, name='news_search'),
    url(r'^ajax/filter_news/$', news_ajaxs.filter_news,name='filter_news'),
    re_path(r'^news/post/(?P<id>[0-9a-zA-Z-_]+)/$', news_views.news_detail, name='news_detail'),
    path('article/list/', news_views.news_list, name='news_list'),
    path('article/add/', news_views.news_add, name='news_add'),
    re_path('article/delete/attachment/(?P<id>[0-9a-zA-Z-_]+)',news_views.delete_attach, name = 'delete_attach'),
    re_path(r'^article/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', news_views.news_update, name='news_update'),
    path('news/archive/<int:year>/',
         news_views.ArticleYearArchiveView.as_view(),
         name="article_year_archive"),
    path('news/archive/<int:year>/<int:month>/',
         news_views.ArticleMonthArchiveView.as_view(month_format='%m'),
         name="archive_month_numeric"),

    #Services
    path('services/', portfolio_views.services, name='services'),
    path('services/list/', portfolio_views.services_list, name='services_list'),
    path('services/add/', portfolio_views.services_add, name='services_add'),
    re_path(r'^services/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', portfolio_views.services_update, name='services_update'),
    url(r'^ajax/addform_servicephoto/$', prf_ajaxs.addform_servicephoto,name="addform_servicephoto"),
    url(r'^ajax/filter_service/$', prf_ajaxs.filter_service,name='filter_service'),
    url(r'^ajax/view_service/$', prf_ajaxs.view_service,name="view_service"),

    #Gallery
    path('list_event/', gallery_views.list_event, name='list_event'),
    path('gallery/list/', gallery_views.gallery_list, name='gallery_list'),
    path('gallery/add/', gallery_views.gallery_add, name='gallery_add'),
    re_path(r'^gallery/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', gallery_views.gallery_update, name='gallery_update'),
    url(r'^ajax/filter_gallery/$', gal_ajaxs.filter_gallery,name='filter_gallery'),
    url(r'^ajax/view_gallery/$', gal_ajaxs.view_gallery,name="view_gallery"),
    re_path(r'^gallery/category/(?P<category>\w+)/$', gallery_views.gallery_category, name='gallery_category'),

    #Contact Us
    path('contact/', profile_views.contact_us, name='contact_us'),
    path('contact/update/', profile_views.contact_update, name='contact_update'),
    path('contact/submit/', profile_views.contact_submit,name='contact_submit'),

    #FAQ
    path('faq/list/', profile_views.faq_list, name='faq_list'),
    path('faq/add/', profile_views.faq_add, name='faq_add'),
    re_path(r'^faq/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', profile_views.faq_update, name='faq_update'),

    #Career
    # path('career/', career_views.career, name='career'),
    # path('career/list/', career_views.career_list, name='career_list'),
    # path('career/add/', career_views.career_add, name='career_add'),
    # re_path(r'^career/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', career_views.career_update, name='career_update'),
    # path('career/photo/list/', career_views.career_photo_list, name='career_photo_list'),
    # path('career/photo/add/', career_views.career_photo_add, name='career_photo_add'),
    # re_path(r'^career/photo/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', career_views.career_photo_update, name='career_photo_update'),
    # path('career/detail/list/', career_views.career_detail_list, name='career_detail_list'),
    # path('career/detail/add/', career_views.career_detail_add, name='career_detail_add'),
    # re_path(r'^career/detail/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', career_views.career_detail_update, name='career_detail_update'),

    #Team
    path('team/list/', team_views.team_list, name='team_list'),
    path('team/add/', team_views.team_add, name='team_add'),
    re_path(r'^team/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', team_views.team_update, name='team_update'),
    path('team/', fe_views.ourteam, name='ourteam'),

    #Testimony
    path('testimony/list/', portfolio_views.testimony_list, name='testimony_list'),
    path('testimony/add/', portfolio_views.testimony_add, name='testimony_add'),
    re_path(r'^testimony/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', portfolio_views.testimony_update, name='testimony_update'),

    #Client
    path('client/list/', portfolio_views.client_list, name='client_list'),
    path('client/add/', portfolio_views.client_add, name='client_add'),
    re_path(r'^client/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', portfolio_views.client_update, name='client_update'),

    #Technology
    path('tech/list/', profile_views.tech_list, name='tech_list'),
    path('tech/add/', profile_views.tech_add, name='tech_add'),
    re_path(r'^tech/update/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', profile_views.tech_update, name='tech_update'),

    #Complaint
    path('complaint/', complaint_views.complaint_page, name='complaint_page'),
    path('complaint/category/', complaint_views.complaint_category_list, name='complaint_category_list'),
    path('complaint/category/add/', complaint_views.complaint_category_add, name='complaint_category_add'),
    re_path(r'^complaint/category/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', complaint_views.complaint_category_update, name='complaint_category_update'),
    path('complaint/list/', complaint_views.complaint_list, name='complaint_list'),
    re_path(r'^complaint/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', complaint_views.complaint_view, name='complaint_view'),
    url(r'^ajax/complaint_response_update/$', complaint_ajaxs.complaint_response_update,name="complaint_response_update"),

    #FINANCE
    path('coa/group/', finn.coa_group_list, name='coa_group_list'),
    path('coa/group/add/', finn.coa_group_add, name='coa_group_add'),
    re_path(r'^coa/group/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', finn.coa_group_update, name='coa_group_update'),

    path('coa/', finn.coa_list, name='coa_list'),
    path('coa/add/', finn.coa_add, name='coa_add'),
    re_path(r'^coa/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', finn.coa_update, name='coa_update'),

    path('general_ledger/', finn.show_general_ledger, name='general_ledger'),
    #GL change to Transaction Book
    # path('gl/', finn.general_ledger_list, name='gl_list'),
    # path('gl/add/', finn.general_ledger_add, name='gl_add'),
    #re_path(r'^gl/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', finn.general_ledger_update, name='gl_update'),
    url(r'^ajax/filter_gl_by_date/$', fin_ajaxs.filter_gl_by_date,name="filter_gl_by_date"),
    url(r'^ajax/filter_gl_by_month/$', fin_ajaxs.filter_gl_by_month,name="filter_gl_by_month"),

    #General Ledger Aktif
    path('transaction/book/', finn.transaction_book_list, name='transaction_book_list'),
    path('transaction/book/update/', finn.transaction_book_update, name='transaction_book_update'),
    url(r'^ajax/addform_gl/$', fin_ajaxs.addform_gl,name="addform_gl"),
    url(r'^ajax/delete_gl/$', fin_ajaxs.delete_gl,name="delete_gl"),
    re_path(r'^print/khotbah/jumat/(?P<start_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<end_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<pass_code>\w+)/$', 
            fin_prints.print_khotbah_jumat, name="print_khotbah_jumat"),
    re_path(r'^print/keuangan/(?P<start_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<end_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<pass_code>\w+)/$', 
            fin_prints.print_keuangan, name="print_keuangan"),

    #Catatan Ringkasan Mingguan
    path('journal/week/', finn.week_journal_list, name='week_journal_list'),
    path('journal/week/update/', finn.week_journal_update, name='week_journal_update'),
    url(r'^ajax/addform_journal_week/$', fin_ajaxs.addform_week_journal,name="addform_week_journal"),
    url(r'^ajax/delete_week_journal/$', fin_ajaxs.delete_week_journal,name="delete_week_journal"),

    #WALLPAPER
    path('wallpaper/', info.show_wallpaper, name='show_wallpaper'),
    url(r'^ajax/synch_jadwal_sholat/$', info_ajaxs.synch_jadwal_sholat,name="synch_jadwal_sholat"),
    path('wallpaper2/', info.show_wallpaper2, name='show_wallpaper2'),
    path('standbywallpaper/', info.show_wallpaper3, name='show_wallpaper3'),
    url(r'^ajax/get_random_slide/$', info_ajaxs.get_random_slide, name='get_random_slide'),
    path('iqamah/', team_views.iqamah_update, name='iqamah_update'),
    path('sliderjumat/', info.show_slider_jumat, name='show_slider_jumat'),
    path('standbywallpaperold/', info.show_standby_wallpaper, name='show_standby_wallpaper'),

    #INFORMATION
    path('rekening/', info.show_rekening, name='show_rekening'),
    path('rekening/list/', info.rekening_list, name='rekening_list'),
    path('rekening/add/', info.rekening_add, name='rekening_add'),
    re_path(r'^rekening/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', info.rekening_update, name='rekening_update'),
    url(r'^ajax/add_rekening_detail/$', info_ajaxs.add_rekening_detail,name="add_rekening_detail"),

    #KUTIPAN
    path('kutipan/', info.show_kutipan, name='show_kutipan'),
    path('kutipan/list/', info.kutipan_list, name='kutipan_list'),
    path('kutipan/add/', info.kutipan_add, name='kutipan_add'),
    re_path(r'^kutipan/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', info.kutipan_update, name='kutipan_update'),
    url(r'^ajax/add_kutipan_detail/$', info_ajaxs.add_kutipan_detail,name="add_kutipan_detail"),

    #KHUTBAH JUMAT
    path('khutbah/', info.show_khutbah, name='show_khutbah'),
    path('khutbah/list/', info.khutbah_list, name='khutbah_list'),
    path('khutbah/add/', info.khutbah_add, name='khutbah_add'),
    re_path(r'^khutbah/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', info.khutbah_update, name='khutbah_update'),
    url(r'^ajax/add_khutbah_detail/$', info_ajaxs.add_khutbah_detail,name="add_khutbah_detail"),

    #KEGIATAN MASJID
    path('kegiatan/', info.show_kegiatan, name='show_kegiatan'),
    path('kegiatan/list/', info.kegiatan_list, name='kegiatan_list'),
    path('kegiatan/add/', info.kegiatan_add, name='kegiatan_add'),
    re_path(r'^kegiatan/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', info.kegiatan_update, name='kegiatan_update'),
    url(r'^ajax/add_kegiatan_detail/$', info_ajaxs.add_kegiatan_detail,name="add_kegiatan_detail"),
    url(r'^ajax/view_kegiatan/$', info_ajaxs.view_kegiatan,name="view_kegiatan"),

    path('naration/', team_views.naration_update, name='naration_update'),

    # Show kegiatan zakat   
    # path('kegiatan_akuntasi/', keg.show_kegiatan_transaksi, name='kegiatan_akuntasi'),
    # url(r'^ajax/filter_gl_by_date_zakat/$', keg_ajaxs.filter_gl_by_date,name="filter_gl_by_date_zakat"),
    # url(r'^ajax/filter_gl_by_month_zakat/$', keg_ajaxs.filter_gl_by_month,name="filter_gl_by_month_zakat"),

    # New Kegiatan Zakat
    # path('transaction/zakat/', keg.kegiatan_transaksi_list, name='transaction_zakat_list'),
    # path('transaction/zakat/update/', keg.kegiatan_transaksi_update, name='transaction_zakat_update'),
    # url(r'^ajax/addform_kg/$', keg_ajaxs.addform_gl,name="addform_kg"),
    # url(r'^ajax/delete_kg/$', keg_ajaxs.delete_gl,name="delete_kg"),
#     re_path(r'^print/khotbah/jumats/(?P<start_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<end_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<pass_code>\w+)/$', 
#             keg_prints.print_khotbah_jumat, name="print_khotbah_jumats"),
    # re_path(r'^print/kegiatan/(?P<start_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<end_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<pass_code>\w+)/$', 
    #        keg_prints.print_ringkasan_zakat, name="print_ringkasan"),
    # re_path(r'^print/keuangan/kegiatan(?P<start_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<end_date>[0-9]{2}-?[0-9]{2}-?[0-9]{4})/(?P<pass_code>\w+)/$', 
    #        keg_prints.print_keuangan_zakat, name="print_keuangan_kegiatan"),
    
    # coa zakat
    # path('coa/group/zakat/', keg.coa_group_list, name='coa_group_list'),
    # path('coa/group/zakat/add/', keg.coa_group_add, name='coa_group_add'),
    # re_path(r'^coa/group/zakat/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', keg.coa_group_update, name='coa_group_update'),

    # path('coa/zakat/', keg.coa_list, name='coa_list'),
    # path('coa/zakat/add/', keg.coa_add, name='coa_add'),
    # re_path(r'^coa/zakat/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', keg.coa_update, name='coa_update'),
    
    # #qurban
    # path('qurban/', qurban.qurban_list, name='qurban_list'),
    # re_path(r'^qurban/update/$', qurban.qurban_update, name='qurban_update'),
    
    # path('qurban/type/', qurban.qurban_type_list, name='qurban_type_list'),
    # path('qurban/type/add/', qurban.qurban_type_add, name='qurban_type_add'),
    # re_path(r'^qurban/type/(?P<status>\w+):(?P<id>[0-9a-zA-Z-_]+)/$', qurban.qurban_type_update, name='qurban_type_update'),
    # url(r'^ajax/addform_qurban/$', qurban_ajaxs.addform_qurban,name="addform_qurban"),
    # url(r'^ajax/delete_qurban/$', qurban_ajaxs.delete_qurban,name="delete_qurban"),


    # ===== Mobile =====

    path('mobile/login/', mobile_auth.login_user, name='mobile_login_user'),
    path('mobile/list_events/', mobile_event.list_events, name='mobile_list_events'),
    path('mobile/event_detail/', mobile_event.event_detail, name='mobile_event_detail'),
    path('mobile/check_participant/', mobile_event.check_participant, name='mobile_check_participant'),

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

handler404 = auth_views.handler404
handler500 = auth_views.handler500
handler403 = auth_views.handler403
handler400 = auth_views.handler400