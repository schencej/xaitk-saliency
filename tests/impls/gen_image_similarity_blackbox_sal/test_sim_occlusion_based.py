import numpy as np
from typing import Dict, Any, Iterable
import unittest.mock as mock
import gc

from smqtk_descriptors.interfaces.image_descriptor_generator import ImageDescriptorGenerator
from smqtk_core.configuration import configuration_test_helper

from xaitk_saliency import PerturbImage, GenerateDescriptorSimilaritySaliency
from xaitk_saliency.impls.gen_image_similarity_blackbox_sal.occlusion_based import PerturbationOcclusion
from xaitk_saliency.utils.masking import occlude_image_batch


class TestPerturbationOcclusion:

    def teardown(self) -> None:
        # Collect any temporary implementations so they are not returned during
        # later `*.get_impl()` requests.
        gc.collect()

    def test_configuration(self) -> None:
        """
        Test configuration suite using stub implementations.
        """

        class StubPI (PerturbImage):
            perturb = None  # type: ignore

            def __init__(self, stub_param: int):
                self.p = stub_param

            def get_config(self) -> Dict[str, Any]:
                return {'stub_param': self.p}

        class StubGen (GenerateDescriptorSimilaritySaliency):
            generate = None  # type: ignore

            def __init__(self, stub_param: int):
                self.p = stub_param

            def get_config(self) -> Dict[str, Any]:
                return {'stub_param': self.p}

        inst = PerturbationOcclusion(
            StubPI(4),
            StubGen(8),
            threads=27
        )
        for inst_i in configuration_test_helper(inst):
            assert inst_i._threads == 27
            assert isinstance(inst_i._perturber, StubPI)
            assert inst_i._perturber.p == 4
            assert isinstance(inst_i._generator, StubGen)
            assert inst_i._generator.p == 8

    def test_generate_success(self) -> None:
        """
        Test successfully invoking _generate().
        """
        class StubPI (PerturbImage):
            """
            Stub perturber that returns masks of ones.
            """

            def perturb(self, ref_image: np.ndarray) -> np.ndarray:
                return np.ones((3, *ref_image.shape[:2]), dtype=bool)

            get_config = None  # type: ignore

        class StubGen (GenerateDescriptorSimilaritySaliency):
            """
            Stub saliency generator that returns zeros with correct shape.
            """

            def generate(
                self,
                ref_descr_1: np.ndarray,
                ref_descr_2: np.ndarray,
                perturbed_descrs: np.ndarray,
                perturbed_masks: np.ndarray,
            ) -> np.ndarray:
                return np.zeros(perturbed_masks.shape[1:], dtype=np.float16)

            get_config = None  # type: ignore

        class StubDescGen (ImageDescriptorGenerator):
            """
            Stub image descriptor generator that returns known feature vectors.
            """

            def generate_arrays_from_images(
                self,
                img_mat_iter: Iterable[np.ndarray]
            ) -> Iterable[np.ndarray]:
                for _ in img_mat_iter:
                    yield np.ones((25))

            get_config = None  # type: ignore

        test_pi = StubPI()
        test_gen = StubGen()
        test_desc_gen = StubDescGen()

        test_ref_img = np.ones((50, 50, 3))
        test_query_img = np.ones((80, 60))

        # Call with default fill
        with mock.patch(
            'xaitk_saliency.impls.gen_image_similarity_blackbox_sal.occlusion_based.occlude_image_batch',
            wraps=occlude_image_batch
        ) as m_occ_img:
            inst = PerturbationOcclusion(test_pi, test_gen)
            test_result = inst._generate(
                test_ref_img,
                test_query_img,
                test_desc_gen
            )

            assert test_result.shape == (80, 60)
            # The "fill" kwarg passed to occlude_image_batch should match
            # the default given, which is None
            m_occ_img.assert_called_once()
            # Using [-1] indexing for compatibility with python 3.7
            m_kwargs = m_occ_img.call_args[-1]
            assert "fill" in m_kwargs
            assert m_kwargs['fill'] is None

        # test with specified fill
        test_fill = 72
        with mock.patch(
            'xaitk_saliency.impls.gen_image_similarity_blackbox_sal.occlusion_based.occlude_image_batch',
            wraps=occlude_image_batch
        ) as m_occ_img:
            inst = PerturbationOcclusion(test_pi, test_gen)
            inst.fill = test_fill
            test_result = inst._generate(
                test_ref_img,
                test_query_img,
                test_desc_gen
            )

            assert test_result.shape == (80, 60)
            # The "fill" kwarg passed to occlude_image_batch should match
            # the default given, which is None
            m_occ_img.assert_called_once()
            # Using [-1] indexing for compatibility with python 3.7
            m_kwargs = m_occ_img.call_args[-1]
            assert "fill" in m_kwargs
            assert m_kwargs['fill'] == test_fill
