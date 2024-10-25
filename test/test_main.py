import os
import pytest
import pywebcoos


def test_invalid_api_token_raises_exception():    
    with pytest.raises(ValueError, match="API access token is not valid."):
        api = pywebcoos.API(token='Invalid token')

def test_invalid_camera_raises_exception():
    key = os.getenv('API_KEY')
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.get_products('Not a camera')
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.get_inventory('Not a camera','video-archive')
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.download('Not a camera','video-archive','202401011000','202401011010',1,'.')

def test_invalid_product_raises_exception():
    key = os.getenv('API_KEY')
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Requested product is not available at this camera."):
        api.get_inventory('Charleston Harbor, SC','Not a product')
    with pytest.raises(ValueError, match="Requested product is not available at this camera."):
        api.download('Charleston Harbor, SC','Not a product','202401011000','202401011010',1,'.')

def test_invalid_date_format_raises_exception():
    key = os.getenv('API_KEY')
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Requested start date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC','video-archive','20241101200','202401101200',1,'.')  
    with pytest.raises(ValueError, match="Requested stop date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC','video-archive','202401101200','20241101200',1,'.')  
    with pytest.raises(ValueError, match="Requested start date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC','video-archive','01/01/2024 10:00','01/01/2024 10:30',1,'.')          
        
def test_date_out_of_range_raises_exception():
    key = os.getenv('API_KEY')
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="At least one requested date bound is outside the range of available data for this product at this camera."):
        api.download('Charleston Harbor, SC','video-archive','190001011000','190001011010',1,'.')  
        


def test_video_download():
    key = os.getenv('API_KEY')
    api = pywebcoos.API(str(key))
    fname = api.download('Charleston Harbor, SC',
                         'video-archive',
                         '202401011000',
                         '202401011010',
                         1,
                         '.')
    assert len(fname)>0 , 'Video download failed.'
    os.remove('nwlon_charleston-2024-01-01-150123Z.mp4')

