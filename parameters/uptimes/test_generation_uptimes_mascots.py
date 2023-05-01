import unittest
from unittest import mock

from experiment_files.parameters.uptimes import generation_uptimes_mascots
from unittest.mock import *

from experiment_files.parameters.uptimes import generation_uptimes_mascots
import numpy

class TestGenerateOverlapsDistributionFromUptimes:
    def test_nominal(self):
        mock_uptimes_distrib_per_node = [
            [(50,1), -1, (300, 1)],  # Server
            [(0,0), (150, 2), -1]   # Dep0
        ]


class TestGetMatchingRounds(unittest.TestCase):
    def test_nominal(self):
        uptimes_server = [(50, 1), -1, (300, 1), -1]
        uptimes_dep = [(0,0), (150, 2), -1, -1]

        res = generation_uptimes_mascots._get_matching_rounds(uptimes_server, uptimes_dep)

        expected_result = [0]
        self.assertEqual(res, expected_result)


class TestGenerateOverlapDistributionPerDep(unittest.TestCase):
    @mock.patch.object(generation_uptimes_mascots, "random_generator")
    @mock.patch.object(generation_uptimes_mascots, "_get_matching_rounds")
    def test_nominal(self, mock_get_matching_rounds, mock_random_generator):
        mock_uptimes_distrib_per_node = [
            [(50, 1), -1, (300, 1), (493,2)],  # Server
            [(0, 0), (150, 2), -1, -1],   # Dep0
            [-1, (150, 2), (500,2), (530, 2)]   # Dep1
        ]
        mock_matching_rounds = [[2,3], [2]]
        mock_get_matching_rounds.side_effect = mock_matching_rounds
        mock_random_generator.choice = MagicMock()
        mock_random_generator.choice.side_effect = [[3], [2]]

        res = generation_uptimes_mascots._generate_overlap_distribution_per_dep(mock_uptimes_distrib_per_node, total_nb_overlaps_deps=30)

        expected_res = [[3], [2]]

        self.assertEqual(res, expected_res)
        mock_get_matching_rounds.assert_has_calls([
            call([(50, 1), -1, (300, 1), (493,2)], [(0, 0), (150, 2), -1, -1]),
            call([(50, 1), -1, (300, 1), (493,2)], [-1, (150, 2), (500,2), (530, 2)]),
        ])
        mock_random_generator.choice.assert_has_calls([
            call([2,3], 30, replace=False),
            call([2], 30, replace=False),
        ])



