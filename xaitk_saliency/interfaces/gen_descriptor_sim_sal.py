import abc

import numpy as np
from smqtk_core import Plugfigurable


class GenerateDescriptorSimilaritySaliency (Plugfigurable):
    """
    Visual saliency map generation interface whose implementations transform
    black-box feature-vectors from multiple references and perturbations into
    saliency heatmaps.

    This transformation requires two reference images, translated into
    feature-vectors via some black-box means, between which we are trying to
    discern the feature-space saliency.
    This also requires the feature-vectors for perturbed images as well as the
    masks of the perturbations as would be output from a
    :class:`xaitk_saliency.interfaces.perturb_image.PerturbImage`
    implementation.
    We expect perturbations to be relative to the query image.
    """

    @abc.abstractmethod
    def generate(
        self,
        ref_descr: np.ndarray,
        query_descr: np.ndarray,
        perturbed_descrs: np.ndarray,
        perturbed_masks: np.ndarray,
    ) -> np.ndarray:
        """
        Generate a visual saliency heatmap matrix given the black-box
        descriptor generation output on two reference images, the same
        descriptor output on perturbed images and the masks of the visual
        perturbations.

        Perturbation mask input into the `perturbed_masks` parameter here is
        equivalent to the perturbation mask output from a
        :meth:`xaitk_saliency.interfaces.perturb_image.PerturbImage.perturb`
        method implementation.
        We expect perturbations to be relative to the second reference image.
        These should have the shape `[nMasks x H x W]`, and values in range
        [0, 1], where a value closer to 1 indicates areas of the image that
        are *unperturbed*.
        Note the type of values in masks can be either integer, floating point
        or boolean within the above range definition.
        Implementations are responsible for handling these expected variations.

        Generated saliency heatmap matrices should be floating-point typed and
        be composed of values in the [-1,1] range.
        Positive values of the saliency heatmaps indicate regions which increase
        image similarity scores, while negative values indicate regions which
        decrease image similarity scores according to the model that generated
        input feature vectors.

        :param ref_descr:
            Reference image float feature-vector, shape `[nFeats]`
        :param query_descr:
            Query image float feature-vector, shape `[nFeats]`.
        :param perturbed_descrs:
            Feature vectors of query image perturbations, float typed of shape
            `[nMasks x nFeats]`.
        :param perturbed_masks:
            Perturbation masks `numpy.ndarray` over the query image.
            This should be parallel in association to the `perturbed_descrs`
            parameter.
            This should have a shape `[nMasks x H x W]`, and values in range
            [0, 1], where a value closer to 1 indicates areas of the image that
            are *unperturbed*.
        :return: Generated saliency heatmap as a float-typed `numpy.ndarray`
            with shape `[H x W]`.
        """

    def __call__(
        self,
        ref_descr: np.ndarray,
        query_descr: np.ndarray,
        perturbed_descrs: np.ndarray,
        perturbed_masks: np.ndarray,
    ) -> np.ndarray:
        """
        Alias for :meth:`.GenerateDescriptorSimilaritySaliency.generate`.
        """
        return self.generate(
            ref_descr,
            query_descr,
            perturbed_descrs,
            perturbed_masks
        )
