import datetime
from dateutil.parser import parse
import cgi
from bson.objectid import ObjectId
from helper_functions import *


class Post:

    def __init__(self, default_config):
        self.collection = default_config['POSTS_COLLECTION']
        self.response = {'error': None, 'data': None}
        self.debug_mode = default_config['DEBUG']

    def get_posts(self, limit, skip, tag=None, search=None):
        self.response['error'] = None
        cond = {}
        if tag is not None:
            cond = {'tags': tag}
        elif search is not None:
            cond = {'$or': [
                    {'title': {'$regex': search, '$options': 'i'}},
                    {'description': {'$regex': search, '$options': 'i'}}]}
        try:
            cursor = self.collection.find(cond).sort(
                'date', direction=-1).skip(skip).limit(limit)
            self.response['data'] = []
            for post in cursor:
                if 'tags' not in post:
                    post['tags'] = []
                if 'comments' not in post:
                    post['comments'] = []

                self.response['data'].append({
                    'id': post['_id'],
                    'incident_title': post['title'],
                    'incident_short_description': post['incident_short_description'],
                    'incident_description': post['incident_description'],
                    'ttp_resource_infrastructure': post['ttp_resource_infrastructure'],
                    'incident_categories': post['incident_categories'],
                    'ttp_description': post['ttp_description'],
                    'ttp_exploits_targets': post['ttp_exploits_targets'],
                    'incident_time_initial_compromise': post['incident_time_initial_compromise'],
                    'incident_time_incident_reported': post['incident_time_incident_reported'],

                    'loss_crypto': post['loss-crypto'],
                    'loss_usd': post['loss_usd'],
                    'description_geographical': post['description_geographical'],
                    'references': post['references'],
                    'date': post['date'],
                    'permalink': post['permalink'],
                    'author': post['author'],
                    'comments': post['comments']})

        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Posts not found..'

        return self.response

    def get_post_by_permalink(self, permalink):
        self.response['error'] = None
        try:
            self.response['data'] = self.collection.find_one(
                {'permalink': permalink})
        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Post not found..'

        return self.response

    def get_post_by_id(self, post_id):
        self.response['error'] = None
        try:
            self.response['data'] = self.collection.find_one(
                {'_id': ObjectId(post_id)})
            if self.response['data']:
                if 'tags' not in self.response['data']:
                    self.response['data']['tags'] = ''
                else:
                    self.response['data']['tags'] = ','.join(
                        self.response['data']['tags'])
        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Post not found..'

        return self.response

    def get_total_count(self, tag=None, search=None):
        cond = {}
        if tag is not None:
            cond = {'tags': tag}
        elif search is not None:
            cond = {'$or': [
                    {'title': {'$regex': search, '$options': 'i'}},
                    {'description': {'$regex': search, '$options': 'i'}}]}

        return self.collection.find(cond).count()

    def get_tags(self):
        self.response['error'] = None
        try:
            self.response['data'] = list(self.collection.aggregate([
                {'$unwind': '$tags'},
                {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10},
                {'$project': {'title': '$_id', 'count': 1, '_id': 0}}
            ]))
        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Get tags error..'

        return self.response

    def create_new_post(self, post_data):
        self.response['error'] = None
        try:
            self.response['data'] = self.collection.insert(post_data)
        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Adding post error..'

        return self.response

    def edit_post(self, post_id, post_data):
        self.response['error'] = None

        del post_data['date']
        #del post_data['permalink']

        try:
            self.collection.update(
                {'_id': ObjectId(post_id)}, {"$set": post_data}, upsert=False)
            self.response['data'] = True

        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Post update error..'

        return self.response

    def delete_post(self, post_id):
        self.response['error'] = None
        try:
            if self.get_post_by_id(post_id) and self.collection.remove({'_id': ObjectId(post_id)}):
                self.response['data'] = True
            else:
                self.response['data'] = False
        except Exception as e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Deleting post error..'

        return self.response

    @staticmethod
    def validate_post_data(post_data):
        """
        Validates post data by converting &, <, > into
        HTML safe sequences. Appends permalink to the post_data

        :param post_data:
            Dictionary of post data consists of the following string keys:
                'id'
                'incident_title'
                'incident_short_description'
                'incident_description'
                'ttp_resource_infrastructure'
                'incident_categories'
                'ttp_description'
                'ttp_exploits_targets'
                'incident_time_initial_compromise'
                'incident_time_incident_reported'
                'loss_crypto'
                'loss_usd'
                'description_geographical'
                'references'
                'author'
                'comments'

        :type post_data: dictionary

        :return: post_data with escaped fields + permalink + date
            Dictionary of out post data consists of the following string keys:
                'id'
                'incident_title'
                'incident_short_description'
                'incident_description'
                'ttp_resource_infrastructure'
                'incident_categories'
                'ttp_description'
                'ttp_exploits_targets'
                'incident_time_initial_compromise'
                'incident_time_incident_reported'
                'loss_crypto'
                'loss_usd'
                'description_geographical'
                'references'
                'author'
                'comments'
            ADDED by this method
            +   'date'
            +   'permalink'

        :rtype: dictionary
        """
        # 26 ascii_uppercase + 10 digit
        # 12 characters 
        # 4.7383813e+18 possible combinations 
        # Quite unlikely for a collision to happen
        permalink = random_string(12)


        # Escape user input fields
        post_data['incident_title'] = cgi.escape(post_data['incident_title'])
        post_data['incident_short_description'] = cgi.escape(post_data['incident_short_description'], quote=True)
        post_data['incident_description'] = cgi.escape(post_data['incident_description'], quote=True)
        post_data['ttp_resource_infrastructure'] = cgi.escape(post_data['ttp_resource_infrastructure'])
        post_data['incident_categories'] = cgi.escape(post_data['incident_categories'])
        post_data['ttp_description'] = cgi.escape(post_data['ttp_description'])
        post_data['ttp_exploits_targets'] = cgi.escape(post_data['ttp_exploits_targets'])

        try:
            post_data['incident_time_initial_compromise'] = \
                parse(cgi.escape(post_data['incident_time_initial_compromise']))

        # Put as None if there is a bug
        except:
            post_data['incident_time_initial_compromise'] = None

        try:
            post_data['incident_time_incident_reported'] = \
                parse((post_data['incident_time_incident_reported']))

        # Put as None if there is a bug
        except:
            post_data['incident_time_incident_reported'] = None

        post_data['loss_crypto'] = cgi.escape(post_data['loss_crypto'])
        post_data['loss_usd'] = cgi.escape(post_data['loss_usd'])
        post_data['description_geographical'] = cgi.escape(post_data['description_geographical'])
        post_data['references'] = cgi.escape(post_data['references'])

        # append to to post_data
        post_data['date'] = datetime.datetime.utcnow()
        post_data['permalink'] = permalink

        print(post_data)

        return post_data

    @staticmethod
    def print_debug_info(msg, show=False):
        if show:
            import sys
            import os

            error_color = '\033[32m'
            error_end = '\033[0m'

            error = {'type': sys.exc_info()[0].__name__,
                     'file': os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename),
                     'line': sys.exc_info()[2].tb_lineno,
                     'details': str(msg)}

            print(error_color)
            print('\n\n---\nError type: %s in file: %s on line: %s\nError \
                  details: %s\n---\n\n'\
                  % (error['type'], error['file'], error['line'],
                     error['details']))
            print(error_end)
