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

                self.response['data'].append({'id': post['_id'],
                                              'title': post['title'],
                                              # 'short-description': post['short-description'],
                                              'description': post['description'],

                                              'blockchain-platform': \
                                                post['blockchain-platform'],

                                              'attack-vector': \
                                                post['attack-vector'],

                                              'vulnerability-exploited': \
                                                post['vulnerability-exploited'],

                                              'loss-crypto': \
                                                post['loss-crypto'],

                                              'loss-usd': \
                                                post['loss-usd'],

                                              'source-of-attack': \
                                                post['source-of-attack'],

                                              'resources': \
                                                post['resources'],

                                              'time-of-attack': \
                                                post['time-of-attack'],

                                              'time-reported': \
                                                post['time-reported'],

                                              'date': post['date'],
                                              'permalink': post['permalink'],
                                              'tags': post['tags'],
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
                'title'
                'short-description'
                'description'
                'blockchain-platform'
                'attack-vector'
                'vulnerability-exploited'
                'loss-crypto'
                'loss-usd'
                'source-of-attack'
                'resources'
                'time-of-attack'
                'time-reported'
                'tags'
                'author'

        :type post_data: dictionary

        :return: post_data with escaped fields + permalink + date
            Dictionary of out post data consists of the following string keys:
                'title'
                'short-description'
                'description'
                'blockchain-platform'
                'attack-vector'
                'vulnerability-exploited'
                'loss-crypto'
                'loss-usd'
                'source-of-attack'
                'resources'
                'time-of-attack'
                'time-reported'
                'tags'
                'author'

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
        post_data['title'] = \
            cgi.escape(post_data['title'])

        post_data['short-description'] = \
                cgi.escape(post_data['short-description'], quote=True)

        post_data['description'] = \
                cgi.escape(post_data['description'], quote=True)

        post_data['blockchain-platform'] = \
            cgi.escape(post_data['blockchain-platform'])

        post_data['attack-vector'] = \
            cgi.escape(post_data['attack-vector'])

        post_data['vulnerability-exploited'] = \
            cgi.escape(post_data['vulnerability-exploited'])

        post_data['loss-crypto'] = \
            cgi.escape(post_data['loss-crypto'])

        post_data['loss-usd'] = \
            cgi.escape(post_data['loss-usd'])

        post_data['source-of-attack'] = \
            cgi.escape(post_data['source-of-attack'])

        post_data['resources'] = \
            cgi.escape(post_data['resources'])

        #TODO convert the string field to date object
        post_data['time-of-attack'] = \
            parse(cgi.escape(post_data['time-of-attack']))

        post_data['time-reported'] = \
            parse((post_data['time-reported']))


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
