from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import News
from django.urls import reverse
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.urls import reverse,resolve
from .views import index, detail_view
from .forms import NewsModelForm
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver


# Create your tests here.
User = get_user_model()
def create_image(filename, size=(100,100), image_mode='RGB', image_formant='PNG'):
    data = BytesIO()
    Image.new(image_mode, size).save(data,image_formant)
    data.seek(0)
    return data
class NewsException(Exception):
    pass

class NewsTest(TestCase):
    def setUp(self):
        admin_user = User(username='admin',email='admin@admin.com')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin')
        admin_user.save()
        self.admin = admin_user
        self.admin_name = 'admin'
        self.admin_password = 'admin'
        registered_user = User(username='registered',email='registered@registered.com')
        registered_user.is_staff = False
        registered_user.is_superuser = False
        registered_user.set_password('registered')
        registered_user.save()
        self.registered = registered_user
        n1 = News.objects.create(
            author = self.admin,
            article ='news 1 article',
            body = 'body 1 article'
        )
        self.registered_name = 'registered'
        self.registered_password = 'registered'
    def test_setup_user_count(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 2)
    def test_all_access_view(self):
        admin_client = Client()
        admin_login = admin_client.login(username=self.admin_name, password = self.admin_password)
        response = admin_client.get(reverse('detail-news', args=(1,)))
        self.assertEqual(response.status_code, 200)
    def test_forbidden_regular_access_view(self):
        self.client.login(username=self.registered_name, password=self.registered_password)
        response = self.client.post('/news/create',{'article': 'denied'})
        self.assertTrue(response.status_code==403)
    def test_allowed_admin_access_view(self):
        self.client.login(username=self.admin_name, password=self.admin_password)
        response = self.client.post('/news/create',{'article':'allowed'})
        self.assertTrue(response.status_code == 200)
        created_news = News.objects.filter(article='allowed')
        self.assertEqual(len(created_news), 1)
    def test_valid_image_upload(self):
        url = '/news/create'
        temp_image = create_image('test_temp.png')
        temp_image_file = SimpleUploadedFile('test_temp_image.png', temp_image.getvalue())
        data = {'article': 'test_image', 'image': temp_image_file}
        self.client.login(username=self.admin_name, password=self.admin_password)
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        news_objects = News.objects.all().count()
        self.assertEqual(news_objects, 2)
        if os.path.exists("staticbase/media/news_images/test_temp_image.png"):
            os.remove("staticbase/media/news_images/test_temp_image.png")
            os.remove("staticbase/media/news_images/test_temp_image_thumb.png")
        else:
            raise NewsException('The file does not exist')
    def test_all_urls(self):
        self.client.login(username=self.admin_name, password=self.admin_password)
        url_index = reverse('index')
        url_detail = reverse('detail-news', args=(1,)) 
        self.assertEqual(resolve(url_index).func, index)
        self.assertEqual(resolve(url_detail).func, detail_view)
        response_index = self.client.get(url_index)
        self.assertTemplateUsed(response_index, 'index.html')
        response_detail = self.client.get(url_detail)
        self.assertTemplateUsed(response_detail, 'news/detail.html')   
    def test_news_form(self):
        valid_form = NewsModelForm(data={
            'article': 'test_news'
        })
        self.assertTrue(valid_form.is_valid())
        invalid_form = NewsModelForm(data={})
        self.assertFalse(invalid_form.is_valid())
        invalid_form_no_article = NewsModelForm(data={
            'article': ''
        })
        self.assertFalse(invalid_form_no_article.is_valid())
        
class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        admin_user = User(username='admin', email='admin@admin.com')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin')
        admin_user.save()
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        cls.selenium = webdriver.Firefox(firefox_binary=binary)
        cls.selenium.implicitly_wait(10)
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    def test_login(self):
        import time
        self.selenium.get(f'{self.live_server_url}/login/')
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        time.sleep(1)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('admin')
        time.sleep(1)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        time.sleep(1)
        nav = self.selenium.find_element_by_class_name('nav-menu')
        nav.screenshot('nav_test_screenshot.png')
        self.assertTrue('admin' in nav.text)
        self.selenium.find_element_by_link_text('Log out').click()
        time.sleep(1)
        nav = self.selenium.find_element_by_class_name('nav-menu')
        self.assertFalse('admin' in nav.text)