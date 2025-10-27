# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 15:32:29 2024

@author: Matthew.Conlin
"""

import datetime
import logging 
import numpy as np
import os
import pandas as pd
import requests
import pytz


class API():

    def __init__(self, token, verbose=False):
        '''
        Class to interface with the WebCOOS API.
        
        args:
        _ _ _ _ _ _ 
        token : str
            Your WebCOOS API access token.
        verbose : bool, optional
            Whether or not to make the API calls verbose in their output. If True, relevant logging
            messages will be shown. If False, only error logging messages will be shown.
            Default is False.
        
        Example usage:
        _ _ _ _ _ _ 
        api = API(token) # Must register on website to get a toeken
        print(api.get_cameras()) 
        fnames = webcoos.download('Charleston Harbor, SC',201901011200 201901011300)
        '''
        # Set the logging level #
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)

        # Establish the base URL and headers for requests #
        self.api_base_url = 'https://app.webcoos.org/webcoos/api/v1'
        self.HEADERS = {
            'Authorization': 'Token '+token,
            'Accept': 'application/json'
        }      
        #Access the json assets via the webcoos API and get the camera list
        self.assets_json = self._make_api_request(self.api_base_url, self.HEADERS)
        if self.assets_json is not None:
            df_cams = self._get_camera_list(self.assets_json)
            self.cameras = df_cams
        else:
            raise ValueError('API access token is not valid.')
               
    def get_cameras(self):
        return self.cameras
    
    def get_products(self, camera_name):
        '''
        Function to view the available products at a camera.
        '''
        self._check_camera_name(camera_name)
        
        feeds = self._get_camera_feeds(camera_name, self.assets_json)
        feed_name = 'raw-video-data'
        products = self._get_camera_products(feed_name, feeds, camera_name)
        product_labels = []
        for product in products:
            product_labels.append(product['data']['common']['label'])  # Returning the product label      
        return product_labels
    
    def get_inventory(self, camera_name, product_name):
        '''
        Function to view available data for a product at a camera.
        '''
        self._check_camera_name(camera_name)
        self._check_product_name(camera_name, product_name)
        
        feeds = self._get_camera_feeds(camera_name, self.assets_json)
        feed_name = 'raw-video-data'
        products = self._get_camera_products(feed_name, feeds, camera_name)
        service_slug, df_inv = self._get_service_slug(product_name, products, feed_name, camera_name, self.api_base_url, self.HEADERS)
        # What is the range of dates with data?
        min_date = df_inv['Bin Start'].min()
        max_date = df_inv['Bin End'].max()
        return [min_date, max_date]
        
    def download(self, camera_name, product_name, start, stop, interval, save_dir):
        '''
        Function to download imagery.
        '''
        start = str(start)
        stop = str(stop)
        
        self._check_camera_name(camera_name)
        self._check_product_name(camera_name, product_name)
        self._check_date_format(start, 'start')
        self._check_date_format(stop, 'stop')
        self._check_date_range(camera_name, product_name, start, stop)

        start = self._local2ISO(start, camera_name)
        stop = self._local2ISO(stop, camera_name)
        feeds = self._get_camera_feeds(camera_name, self.assets_json)
        feed_name = 'raw-video-data'
        products = self._get_camera_products(feed_name, feeds, camera_name)
        service_slug, df_inv = self._get_service_slug(product_name, products, feed_name, camera_name, self.api_base_url, self.HEADERS)
        filtered_elements = self._get_elements(service_slug, start, stop, interval, self.api_base_url, self.HEADERS)
        filenames = self._download_imagery(filtered_elements, save_dir)
        return filenames
    
    def _check_camera_name(self, camera_name):
        if camera_name not in self.get_cameras()['Camera Name'].values:
            raise ValueError('Camera is not an available WebCOOS camera.')
    
    def _check_product_name(self, camera_name, product_name):
        if product_name not in self.get_products(camera_name):
            raise ValueError('Requested product is not available at this camera.')
            
    def _check_date_format(self, date, date_name):
        if len(date) != 12:
            raise ValueError('Requested '+date_name+' date is of improper format. Format should be yyyymmddHHMM.')
        else:
            try:
                datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), int(date[8:10]), int(date[10:12]))
            except ValueError:
                raise ValueError('Requested '+date_name+' date is of improper format. Format should be yyyymmddHHMM.')        
    
    def _check_date_range(self, camera_name, product_name, start, stop):
        starts = self._local2ISO(start, camera_name)
        stops = self._local2ISO(stop, camera_name)
        ss = []
        for s in [starts, stops]:
            ss.append(datetime.datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16])))
            
        dr = self.get_inventory(camera_name, product_name)
        dtr = []
        for d in dr:
            dtr.append(datetime.datetime(int(d[0:4]), int(d[5:7]), int(d[8:10]), int(d[11:13]), int(d[14:16])))
        
        if dtr[0] <= ss[0] <= dtr[1] and dtr[0] <= ss[1] <= dtr[1]:
            pass
        else:
            raise ValueError('At least one requested date bound is outside the range of available data for this product at this camera.')  
            
    def _make_api_request(self, api_base_url, HEADERS):
        '''
        Function to query the webcoos API for available assets
        '''
        response = requests.get(f"{api_base_url}/assets/", headers=HEADERS)

        # Check the status code of the response
        if response.status_code == 200:
            #Return the assets json
            return response.json()
        else:
            # raise error information if the request was not successful
            logging.error(f"Failed to retrieve assets: {response.status_code} {response.text}")
            return None
      
    def _get_camera_list(self, assets_json):
        '''
        Function to get the camera list
        '''
        # Collecting camera names
        camera_names = [asset['data']['common']['label'] for asset in assets_json['results']]

        # Create pandas dataframe
        df_cams = pd.DataFrame(camera_names, columns=['Camera Name'])

        # Return the dataframe
        return df_cams
     
    def _get_camera_feeds(self, camera_name, assets_json):
        '''
        Function to get the camera feeds for a specific camera
        '''
        for asset in assets_json['results']:
            if asset['data']['common']['label'] == camera_name:
                feeds = asset['feeds']
                break
        return feeds

    def _get_camera_products(self, feed_name, feeds, camera_name):
        '''
        Function to get the camera products available for that camera and feed
        '''
        for feed in feeds:
            if feed['data']['common']['label'] == feed_name:
                products = feed['products']
        return products
                        
    def _get_service_slug(self, product_name, products, feed_name, camera_name, api_base_url, HEADERS):
        '''
        Function to get the service slug and print data inventory
        '''
        # go through and find the service_slug for the desired product
        for product in products:
            if product['data']['common']['label'] == product_name:
                logging.info(f"Services for camera '{camera_name}', feed '{feed_name}' and product '{product_name}':")
                services = product['services']
                for service in services:
                    service_slug = service['data']['common']['slug']
                    logging.info(service_slug)  # Printing the service slug
                break

        #Get the data inventory information for the service slug
        inv_url = f"{api_base_url}/services/{service_slug}/inventory/"
        response = requests.get(inv_url, headers=HEADERS)

        # Check the status code of the response and grab the inventory 
        if response.status_code == 200:
            # Grab the response JSON for the inventory
            inventory_json = response.json()
        else:
            # Print error information if the request was not successful
            logging.error(f"Failed to retrieve assets: {response.status_code} {response.text}")

        #Put the data inventory into a dataframe for further analsyis and to provide some basic summary stats
        inventory_data = inventory_json['results'][0]['values']
        df_inv = pd.DataFrame(inventory_data, columns=['Bin Start', 'Has Data?', 'Bin End', 'Count', 'Bytes', 'Data Start', 'Data End'])

        return service_slug, df_inv
    
    def _get_elements(self, service_slug, start_time, end_time, interval_minutes, api_base_url, HEADERS):
        '''
        Function to create and view the download urls or elements
        '''

        params = {
            'starting_after': start_time,
            'starting_before': end_time,
            'service': service_slug
        }

        #Set the base_url now to avoid including elements in the paginated urls
        base_url = f'{api_base_url}/elements/'
        all_elements = []
        page = 1

        #Run through the response for each page, adding to all_elements with the additional results and print updates to the screen
        while True:
            logging.info(f"Fetching page: {page}")
            response = requests.get(base_url, headers=HEADERS, params=params)
            if response.status_code != 200:
                logging.error(f"Failed to fetch page {page}: {response.status_code}")
                break
            data = response.json()
            all_elements.extend(data['results'])
            logging.info(f"Received {len(data['results'])} elements, total elements collected: {len(all_elements)}")

            # Update the URL for the next request or break the loop if no more pages
            next_url = data.get('pagination', {}).get('next')
            if not next_url:
                logging.info("No more pages.")
                break
            base_url = next_url
            params = None  # Ensure subsequent requests don't duplicate parameters
            page += 1

        # Now use the interval_minutes specified to filter the returned elements to only grab the images on certain intervals
        filtered_elements = []
        logging.info("Timestamps of filtered elements")
        for element in all_elements:
            timestamp_str = element['data']['extents']['temporal']['min']
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
            if timestamp.minute % interval_minutes == 0:
                filtered_elements.append(element)
                logging.info(timestamp)
        return filtered_elements

    def _download_imagery(self, filtered_elements, save_dir):
        '''
        Function to download the data.
        '''

        #Now generate the download ulrs for the images
        download_urls = []
        for element in filtered_elements:
            try:
                download_url = element['data']['properties']['url']
                download_urls.append(download_url)
            except KeyError:
                logging.error("Unexpected element structure:", element)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        logging.info("Beginning imagery download")
        filenames = []
        for url in download_urls:
            filename = os.path.join(save_dir, os.path.basename(url))
            filenames.append(filename)
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors
            logging.info('Downloading')
            
            if not os.path.exists(filename):
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                logging.info('Download complete')
        logging.info(f"Download complete. Downloaded {len(download_urls)} images to {save_dir}")

        return filenames
   
    def _local2ISO(self, local_time, camera_name):
        # Get the camera's time zone #
        i_camera = int(np.where(self.cameras['Camera Name'] == camera_name)[0])      
        try:  # Cameras should have a timezone field in their asset lists #
            self.tz = self.assets_json['results'][i_camera]['data']['properties']['timezone']
        except KeyError:  # If a camera doesn't have a timezone field, try to derive it from the name of the camera (looks for a ', CA' type abbrev in the name) #
            try:  # If a camera doesn't have a timezone field, try to derive it from the name of the camera (looks for a ', CA' type abbrev in the name) #
                sbool = [' '+geo_db['state_abbrevs'][i] in camera_name for i in range(50)]
                state = np.array(geo_db['state_abbrevs'])[np.array(sbool)][0]
                tz = geo_db['tzs'][state]
                self.tz = geo_db['tz_formals'][tz[0]][0]
            except ValueError:  # If both methods fail, default to UTC and warn the user #
                self.tz = 'UTC'
                logging.info('Timezone of camera could not be detected or derived, defaulting to UTC.')
            else:
                logging.warning('Camera timezone could not be detected, but was derived from camera name')
        else:
            logging.info('Camera timezone detected')
                
        # Get the full datetime object and assign time zone #
        dt_local = datetime.datetime(int(local_time[0:4]),
                                     int(local_time[4:6]),
                                     int(local_time[6:8]),
                                     int(local_time[8:10]),
                                     int(local_time[10:12]))
        dt_local = pytz.timezone(self.tz).localize(dt_local)
        # Convert to UTC and make ISO #
        dt_utc = dt_local.astimezone(pytz.timezone('UTC'))
        ISO = dt_utc.isoformat()
        return ISO

    
geo_db = {'state_abbrevs': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'],
          'tzs': {'ME': ['Eastern'], 'NH': ['Eastern'], 'MA': ['Eastern'], 'RI': ['Eastern'], 'CT': ['Eastern'],
                  'NY': ['Eastern'], 'NJ': ['Eastern'], 'PA': ['Eastern'], 'DE': ['Eastern'], 'MD': ['Eastern'],
                  'VA': ['Eastern'], 'NC': ['Eastern'], 'SC': ['Eastern'], 'GA': ['Eastern'], 'FL': ['Eastern'], 
                  'AL': ['Central'], 'MS': ['Central'], 'LA': ['Central'], 'TX': ['Central'], 'WA': ['Pacific'],
                  'OR': ['Pacific'], 'CA': ['Pacific'], 'MI': ['Central'], 'IL': ['Central'], 'IN': ['Central'], 
                  'OH': ['Eastern'], 'WI': ['Central'], 'AK': ['Alaska'], 'HI': ['Hawaii']},
          'tz_formals': {'Eastern': ['America/New_York'],
                         'Central': ['America/Chicago'],
                         'Pacific': ['America/Los_Angeles'],
                         'Alaska': ['America/Nome'],
                         'Hawaii': ['US/Hawaii']}}
