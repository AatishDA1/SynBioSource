from django.test import TestCase
from dashboard.models import AllUsers
from dataset.models import DatasetRegistry, Keyword
from django.core.files.uploadedfile import SimpleUploadedFile

# Run with: python manage.py test synbiosource.tests
class ModelTests(TestCase):

    def setUp(self):
        """
        This method sets up the initial conditions for each test.
        It creates a user which will be used in the subsequent tests.
        """
        self.user = AllUsers.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='testpassword'
        )

    def test_user_creation(self):
        """
        This test verifies that a user can be created with the correct attributes.
        It checks the email, full_name, and password attributes of the created user.
        """
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.full_name, 'Test User')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_dataset_registry_creation(self):
        """
        This test verifies that a DatasetRegistry entry can be created.
        It ensures the dataset is associated with the correct user and 
        that the metadata file's title is as expected.
        """
        dataset_file = SimpleUploadedFile("test_data.zip", b"file_content", content_type="application/zip")
        metadata = {
            "basic_identity": {
                "title": "Test Dataset",
                "description": "A test dataset",
                "version": "1.0",
                "keywords": ["test", "dataset", "upload"],
                "license": "CC BY 4.0"
            }
        }

        dataset = DatasetRegistry.objects.create(
            owner=self.user,
            dataset_file=dataset_file,
            metadata_file=metadata
        )

        self.assertEqual(dataset.owner, self.user)
        self.assertEqual(dataset.metadata_file['basic_identity']['title'], 'Test Dataset')

    def test_dataset_registry_update(self):
        """
        This test verifies that a DatasetRegistry entry can be updated.
        It changes the title in the metadata file and checks if the update is correctly saved.
        """
        dataset_file = SimpleUploadedFile("test_data.zip", b"file_content", content_type="application/zip")
        metadata = {
            "basic_identity": {
                "title": "Test Dataset",
                "description": "A test dataset",
                "version": "1.0",
                "keywords": ["test", "dataset", "upload"],
                "license": "CC BY 4.0"
            }
        }

        dataset = DatasetRegistry.objects.create(
            owner=self.user,
            dataset_file=dataset_file,
            metadata_file=metadata
        )

        # Update the title in metadata.
        dataset.metadata_file['basic_identity']['title'] = "Updated Test Dataset"
        dataset.save()

        updated_dataset = DatasetRegistry.objects.get(id=dataset.id)
        self.assertEqual(updated_dataset.metadata_file['basic_identity']['title'], "Updated Test Dataset")

    def test_dataset_registry_deletion(self):
        """
        This test verifies that a DatasetRegistry entry can be deleted.
        It creates a dataset, deletes it, and ensures that it no longer exists in the database.
        """
        dataset_file = SimpleUploadedFile("test_data.zip", b"file_content", content_type="application/zip")
        metadata = {
            "basic_identity": {
                "title": "Test Dataset",
                "description": "A test dataset",
                "version": "1.0",
                "keywords": ["test", "dataset", "upload"],
                "license": "CC BY 4.0"
            }
        }

        dataset = DatasetRegistry.objects.create(
            owner=self.user,
            dataset_file=dataset_file,
            metadata_file=metadata
        )

        dataset_id = dataset.id
        dataset.delete()

        with self.assertRaises(DatasetRegistry.DoesNotExist):
            DatasetRegistry.objects.get(id=dataset_id)

    def test_keyword_creation_and_increment(self):
        """
        This test verifies that a Keyword entry can be created and updated.
        It ensures that the keyword count can be incremented and saved correctly.
        """
        keyword = Keyword.objects.create(name='test', dataset_count=1)
        self.assertEqual(keyword.name, 'test')
        self.assertEqual(keyword.dataset_count, 1)

        # Increment the dataset count.
        keyword.dataset_count += 1
        keyword.save()

        updated_keyword = Keyword.objects.get(id=keyword.id)
        self.assertEqual(updated_keyword.dataset_count, 2)

    def test_keyword_deletion(self):
        """
        This test verifies that a Keyword entry can be deleted.
        It creates a keyword, deletes it, and ensures that it no longer exists in the database.
        """
        keyword = Keyword.objects.create(name='test', dataset_count=1)
        keyword_id = keyword.id
        keyword.delete()

        with self.assertRaises(Keyword.DoesNotExist):
            Keyword.objects.get(id=keyword_id)

if __name__ == '__main__':
    unittest.main()