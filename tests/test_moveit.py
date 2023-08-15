import unittest
import pathlib
if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from tests.context import ServiceBusQueueTrigger1
else:
    from .context import ServiceBusQueueTrigger1
import json

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()



class Testmoveit_api(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        access_request_sample_file = open('tests/access_request.json')
        access_request_sample_data = json.load(access_request_sample_file)
        access_request_sample_file.close()

        cls.mv = ServiceBusQueueTrigger1.moveit_calls.moveit_api(access_request_sample_data)
        cls.pre_saved_access_request_info = access_request_sample_data
        # userid = cls.mv.create_user('test11@noreply.com').json()["id"]
    
        
        cls.cb_test_group_groupid = 306201 
        cls.userid = 'ay9tpw2upkx747g9'  #fullName': 'MoveITAPI'
        cls.pathfinder_parent_folderid = 344583944


    # @classmethod
    # def tearDownClass(cls) -> None:
    #     cls.mv.delete_user(cls.userid)
    #     return super().tearDownClass()


    def test_get_list_of_subfolders(self):
        mv = self.mv.get_list_of_subfolders(self.pathfinder_parent_folderid)
        self.assertIsNotNone(mv)
        self.assertIsInstance(mv,list)


    def test_get_users(self):
        mv = self.mv._get_pages("users", pgnum=1, limit_page_count=1)
        self.assertIsNotNone(mv)
        self.assertIsInstance(mv, list)


    def test_get_groups(self):
        mv = self.mv._get_pages("groups", pgnum=1, limit_page_count=1)
        self.assertIsNotNone(mv)
        self.assertIsInstance(mv, list)


    def test_get_folders(self):
        mv = self.mv._get_pages("folders", pgnum=1, limit_page_count=1)
        self.assertIsNotNone(mv)
        self.assertIsInstance(mv, list)


# there should be a test for every route that the mv.moveit_process_request() can take. 
#       1. add a user to a group
#       2. add a group to a folder
#       3. add a user to a folder
#       4. add a user to a group and a folder
#       5. add a group to a folder and a user to a folder
#       6. add a group to a folder and a user to a group



    # def test_create_user(self):
    #     members= self.mv.get_bulk_list_or_a_records_details("users")
    #     self.assertEqual(len(list(filter(lambda s: s["email"] == 'test11@noreply.com', members))), 1)


    # def test_add_member_to_group(self):
    #     mv.add_member_to_group(cb_test_group_groupid, userid)
    #     members= mv.get_bulk_list_or_a_records_details("groups", cb_test_group_groupid)
    #     self.assertEqual(len(list(filter(lambda s: s["email"] == 'test11@noreply.com', members))), 1)


    # def test_remove_member_from_group(self):
    #     mv.remove_member_from_group(cb_test_group_groupid, userid)
    #     members= self.mv.get_bulk_list_or_a_records_details("groups", cb_test_group_groupid)
    #     self.assertEqual(len(list(filter(lambda s: s["email"] == 'test11@noreply.com', members))), 0)


    # def test_delete_user(self):
    #     self.mv.delete_user(self.userid)
    #     members= self.mv.get_bulk_list_or_a_records_details("users")
    #     self.assertEqual(len(list(filter(lambda s: s["email"] == 'test11@noreply.com', members))), 0)

    # def test_add_group_to_folder_alreadyexists(self):
    #     mv = self.mv.add_group_to_folder(self.cb_test_group_groupid, self.pathfinder_parent_folderid)
    #     self.assertIsNotNone(mv)
    #     self.assertIsInstance(mv,list)
    

if __name__ == '__main__':
    unittest.main()




