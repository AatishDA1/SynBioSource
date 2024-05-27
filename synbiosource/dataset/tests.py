from django.test import TestCase, Client
from django.urls import reverse
from dataset.models import DatasetRegistry, AllUsers

# Run with: python manage.py test dataset.tests
class BrowsePageTest(TestCase):
    """
    Test the browsing and filtering functionality on the dataset browse page.
    """

    def setUp(self):
        """
        Set up test user and create mock datasets with various attributes.
        """
        # Create a test user.
        self.user = AllUsers.objects.create_user(
            email='testuser@example.com',
            password='password123',
            full_name='Test User'
        )
        # Login the test user.
        self.client = Client()
        self.client.login(email='testuser@example.com', password='password123')
        
        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 1',
                    'description': 'Description of Dataset 1',
                    'keywords': 'synthetic,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Synthetically-Generated'
                    },
                    'data_completion': {
                        'dataset_status': 'Complete'
                    },
                    'pre_processing': {
                        'raw_data': 'Yes',
                        'data_cleanliness': {
                            'cleanliness_status': 'Clean'
                        },
                        'labeling': {
                            'labeled': 'Yes'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'format': 'CSV',
                        'dataset_size': 1024,
                        'number_of_files': 10,
                        'average_file_size': 102
                    }
                }
            }
        )

        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 2',
                    'description': 'Description of Dataset 2',
                    'keywords': 'natural,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Naturally-Obtained'
                    },
                    'data_completion': {
                        'dataset_status': 'In Progress'
                    },
                    'pre_processing': {
                        'raw_data': 'No',
                        'data_cleanliness': {
                            'cleanliness_status': 'Partially Clean'
                        },
                        'labeling': {
                            'labeled': 'No'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'format': 'Excel',
                        'dataset_size': 2048,
                        'number_of_files': 20,
                        'average_file_size': 1024
                    }
                }
            }
        )

        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 2',
                    'description': 'Description of Dataset 2',
                    'keywords': 'natural,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Naturally-Obtained'
                    },
                    'data_completion': {
                        'dataset_status': 'In Progress'
                    },
                    'pre_processing': {
                        'raw_data': 'No',
                        'data_cleanliness': {
                            'cleanliness_status': 'Partially Clean'
                        },
                        'labeling': {
                            'labeled': 'No'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'dataset_size': 2048,
                        'number_of_files': 20,
                        'average_file_size': 1024
                    }
                }
            }
        )

    def test_filter_by_data_origin(self):
        """
        Test filtering by data origin.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'data_origin': 'Synthetically-Generated'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_dataset_status(self):
        """
        Test filtering by dataset status.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'dataset_status': 'Complete'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_raw_data(self):
        """
        Test filtering by raw data availability.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'raw_data': 'Yes'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_data_cleanliness(self):
        """
        Test filtering by data cleanliness.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'cleanliness_status': 'Clean'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertContains(response, 'Dataset 2')

    def test_filter_by_labeled(self):
        """
        Test filtering by whether the data is labeled.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'labeled': 'Yes'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_training_split(self):
        """
        Test filtering by training split.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'train_split': 50
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_validation_split(self):
        """
        Test filtering by validation split.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'validation_split': 30
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_test_split(self):
        """
        Test filtering by test split.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'test_split': 20
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_type(self):
        """
        Test filtering by study type.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'study_type': 'Observational'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_start_date(self):
        """
        Test filtering by study start date.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'study_start_date': '2022-01-01'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_end_date(self):
        """
        Test filtering by study end date.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'study_end_date': '2023-01-01'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_instrumentation(self):
        """
        Test filtering by instrumentation used.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'instrumentation': 'Microscope'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_protocols(self):
        """
        Test filtering by protocols used.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'protocols': 'PCR'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_min_samples(self):
        """
        Test filtering by minimum number of samples.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'min_number_of_samples': 10
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_max_samples(self):
        """
        Test filtering by maximum number of samples.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'max_number_of_samples': 100
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_min_participants(self):
        """
        Test filtering by minimum number of participants.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'min_participants': 5
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_max_participants(self):
        """
        Test filtering by maximum number of participants.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'max_participants': 50
        })
        self.assertEqual(response.status_code, 200)
    
    def test_filter_by_file_format(self):
        """
        Test filtering by file format.
        """
        response = self.client.post(reverse('browse-datasets'), {
            'file-format': 'CSV'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

class YourDatasetsPageTest(TestCase):
    """
    Test the browsing and filtering functionality on the 'Your Datasets' page.
    """

    def setUp(self):
        """
        Set up test user and create mock datasets with various attributes.
        """
        # Create a test user.
        self.user = AllUsers.objects.create_user(
            email='testuser@example.com',
            password='password123',
            full_name='Test User'
        )
        # Login the test user.
        self.client = Client()
        self.client.login(email='testuser@example.com', password='password123')
        
        # Create mock datasets with different attributes.
        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 1',
                    'description': 'Description of Dataset 1',
                    'keywords': 'synthetic,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Synthetically-Generated'
                    },
                    'data_completion': {
                        'dataset_status': 'Complete'
                    },
                    'pre_processing': {
                        'raw_data': 'Yes',
                        'data_cleanliness': {
                            'cleanliness_status': 'Clean'
                        },
                        'labeling': {
                            'labeled': 'Yes'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'format': 'CSV',
                        'dataset_size': 1024,
                        'number_of_files': 10,
                        'average_file_size': 102
                    }
                }
            }
        )

        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 2',
                    'description': 'Description of Dataset 2',
                    'keywords': 'natural,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Naturally-Obtained'
                    },
                    'data_completion': {
                        'dataset_status': 'In Progress'
                    },
                    'pre_processing': {
                        'raw_data': 'No',
                        'data_cleanliness': {
                            'cleanliness_status': 'Partially Clean'
                        },
                        'labeling': {
                            'labeled': 'No'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'format': 'Excel',
                        'dataset_size': 2048,
                        'number_of_files': 20,
                        'average_file_size': 1024
                    }
                }
            }
        )

        DatasetRegistry.objects.create(
            owner=self.user,
            metadata_file={
                'basic_identity': {
                    'title': 'Dataset 2',
                    'description': 'Description of Dataset 2',
                    'keywords': 'natural,test'
                },
                'dataset_creation': {
                    'general': {
                        'data_origin': 'Naturally-Obtained'
                    },
                    'data_completion': {
                        'dataset_status': 'In Progress'
                    },
                    'pre_processing': {
                        'raw_data': 'No',
                        'data_cleanliness': {
                            'cleanliness_status': 'Partially Clean'
                        },
                        'labeling': {
                            'labeled': 'No'
                        }
                    }
                },
                'dataset_composition': {
                    'general': {
                        'dataset_size': 2048,
                        'number_of_files': 20,
                        'average_file_size': 1024
                    }
                }
            }
        )

    def test_filter_by_data_origin(self):
        """
        Test filtering by data origin.
        """
        response = self.client.post(reverse('your-datasets'), {
            'data_origin': 'Synthetically-Generated'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_dataset_status(self):
        """
        Test filtering by dataset status.
        """
        response = self.client.post(reverse('your-datasets'), {
            'dataset_status': 'Complete'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_raw_data(self):
        """
        Test filtering by raw data availability.
        """
        response = self.client.post(reverse('your-datasets'), {
            'raw_data': 'Yes'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_data_cleanliness(self):
        """
        Test filtering by data cleanliness.
        """
        response = self.client.post(reverse('your-datasets'), {
            'data_cleanliness': 'Clean'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertContains(response, 'Dataset 2')

    def test_filter_by_labeled(self):
        """
        Test filtering by whether the data is labeled.
        """
        response = self.client.post(reverse('your-datasets'), {
            'labeled': 'Yes'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

    def test_filter_by_training_split(self):
        """
        Test filtering by training split.
        """
        response = self.client.post(reverse('your-datasets'), {
            'train_split': 50
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_validation_split(self):
        """
        Test filtering by validation split.
        """
        response = self.client.post(reverse('your-datasets'), {
            'validation_split': 30
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_test_split(self):
        """
        Test filtering by test split.
        """
        response = self.client.post(reverse('your-datasets'), {
            'test_split': 20
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_type(self):
        """
        Test filtering by study type.
        """
        response = self.client.post(reverse('your-datasets'), {
            'study_type': 'Observational'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_start_date(self):
        """
        Test filtering by study start date.
        """
        response = self.client.post(reverse('your-datasets'), {
            'study_start_date': '2022-01-01'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_study_end_date(self):
        """
        Test filtering by study end date.
        """
        response = self.client.post(reverse('your-datasets'), {
            'study_end_date': '2023-01-01'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_instrumentation(self):
        """
        Test filtering by instrumentation used.
        """
        response = self.client.post(reverse('your-datasets'), {
            'instrumentation': 'Microscope'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_protocols(self):
        """
        Test filtering by protocols used.
        """
        response = self.client.post(reverse('your-datasets'), {
            'protocols': 'PCR'
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_min_samples(self):
        """
        Test filtering by minimum number of samples.
        """
        response = self.client.post(reverse('your-datasets'), {
            'min_number_of_samples': 10
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_max_samples(self):
        """
        Test filtering by maximum number of samples.
        """
        response = self.client.post(reverse('your-datasets'), {
            'max_number_of_samples': 100
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_min_participants(self):
        """
        Test filtering by minimum number of participants.
        """
        response = self.client.post(reverse('your-datasets'), {
            'min_participants': 5
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_max_participants(self):
        """
        Test filtering by maximum number of participants.
        """
        response = self.client.post(reverse('your-datasets'), {
            'max_participants': 50
        })
        self.assertEqual(response.status_code, 200)

    def test_filter_by_file_format(self):
        """
        Test filtering by file format.
        """
        response = self.client.post(reverse('your-datasets'), {
            'file-format': 'CSV'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dataset 1')
        self.assertNotContains(response, 'Dataset 2')

if __name__ == '__main__':
    unittest.main()