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

