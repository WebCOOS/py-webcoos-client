import os
import pytest
import pywebcoos


# Input checking / error handling tests #
def test_invalid_api_token_raises_exception():    
    with pytest.raises(ValueError, match="API access token is not valid."):
        pywebcoos.API(token='Invalid token')

        
def test_invalid_camera_raises_exception():
    key = _get_key()
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.get_products('Not a camera')
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.get_inventory('Not a camera', 'video-archive')
    with pytest.raises(ValueError, match="Camera is not an available WebCOOS camera."):
        api.download('Not a camera', 'video-archive', '202401011000', '202401011010', 1, '.')

        
def test_invalid_product_raises_exception():
    key = _get_key()
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Requested product is not available at this camera."):
        api.get_inventory('Charleston Harbor, SC', 'Not a product')
    with pytest.raises(ValueError, match="Requested product is not available at this camera."):
        api.download('Charleston Harbor, SC', 'Not a product', '202401011000', '202401011010', 1, '.')

        
def test_invalid_date_format_raises_exception():
    key = _get_key()
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="Requested start date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC', 'video-archive', '20241101200', '202401101200', 1, '.')  
    with pytest.raises(ValueError, match="Requested stop date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC', 'video-archive', '202401101200', '20241101200', 1, '.')  
    with pytest.raises(ValueError, match="Requested start date is of improper format. Format should be yyyymmddHHMM."):
        api.download('Charleston Harbor, SC', 'video-archive', '01/01/2024 10:00', '01/01/2024 10:30', 1, '.')          

        
def test_date_out_of_range_raises_exception():
    key = _get_key()
    api = pywebcoos.API(str(key))
    with pytest.raises(ValueError, match="At least one requested date bound is outside the range of available data for this product at this camera."):
        api.download('Charleston Harbor, SC', 'video-archive', '190001011000', '190001011010', 1, '.')  

        
def test_download_videos_for_camera_without_state_in_name_passes():
    key = _get_key()
    api = pywebcoos.API(str(key))
    try:
        fname = api.download('Sausalito - Galilee Harbor',
                             'video-archive',
                             '202510031000',
                             '202510031010',
                             1,
                             '.')
    
        os.remove('sausalito_galilee-2025-10-03-170924Z.mp4')
    except IndexError:
        fname = None
    assert fname is not None , 'Imagery download for Sausalito camera failed because timezone could not be detected'


# Unit tests #
def test_get_cameras():
    key = _get_key()
    api = pywebcoos.API(str(key))
    cams = api.get_cameras()
    assert len(cams) > 0 , 'Getting camera list failed'

    
def test_get_products():
    key = _get_key()
    api = pywebcoos.API(str(key))
    prods = api.get_products('Charleston Harbor, SC')
    assert len(prods) > 0 , 'Getting product list failed'    

    
def test_get_inventory():
    key = _get_key()
    api = pywebcoos.API(str(key))
    inv = api.get_inventory('Charleston Harbor, SC', 'video-archive')
    assert len(inv) > 0 , 'Getting product inventory failed' 

    
def test_download_videos():
    key = _get_key()
    api = pywebcoos.API(str(key))
    fname = api.download('Charleston Harbor, SC',
                         'video-archive',
                         '202501011000',
                         '202501011010',
                         1,
                         '.')
    assert len(fname) > 0 , 'Video download failed.'
    os.remove('nwlon_charleston-2025-01-01-150452Z.mp4')

    
def test_download_images():
    key = _get_key()
    api = pywebcoos.API(str(key))
    fname = api.download('Charleston Harbor, SC',
                         'one-minute-stills',
                         '202501011000',
                         '202501011001',
                         1,
                         '.')
    assert len(fname) > 0 , 'Image download failed.'
    os.remove('nwlon_charleston-2025-01-01-150023Z.jpg')


# Integration test #
def test_function_integration():
    key = _get_key()
    api = pywebcoos.API(str(key))
    cam = api.get_cameras()[api.get_cameras()['Camera Name'] == 'Masonboro Inlet, Wrightsville Beach, NC'].values[0][0]
    prod = api.get_products(cam)[1]
    fname = api.download(cam, prod, 202410011000, 202410011001, 1, '.') 
    assert len(fname) > 0 , 'Image download failed.'
    os.remove('masonboro_inlet-2024-10-01-140036Z.jpg')


def _get_key():
    key = os.getenv('API_KEY')
    if key[0] == "'":
        key = key[1:-1]
    return key
