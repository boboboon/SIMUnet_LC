import tensorflow as tf
from tensorflow.keras.layers import Layer

import numpy as np

class CombineCfacLayer(Layer):
    """
    Creates the combination layer of SIMUnet.
    """

    def __init__(self, scales, linear_names, quad_names):
        """
        Parameters
        ----------
            scales: np.array
                The scales by which to divide each contribution.
            linear_names: list[str]
                A list of names for the operators
            quad_names: list[str]
                A list of names for the quadtaric contributions.
        """
        # Initialise a Layer instance
        if len(scales) != len(linear_names):
            raise ValueError("Scales and linear_names must have the same length")
        if len(linear_names)**2 != len(quad_names):
            raise ValueError("There must be len(linear_names)**2 quad_names")
        super().__init__()

        self.w = tf.Variable(
            initial_value=tf.zeros(shape=(len(scales),), dtype="float32"),
            trainable=True,
        )
        self.scales = np.array(scales, dtype=np.float32)
        self.linear_names = linear_names
        self.quad_names = quad_names

    @property
    def quad_scale_reciprocals(self):
        inv_scale = 1/self.scales
        return np.tril(
            np.outer(inv_scale, inv_scale)
        ).ravel()


    def _compute_linear(self, linear_values):
        scaled_values = linear_values/self.scales[:, np.newaxis]
        return tf.reduce_sum(self.w[:, tf.newaxis] * scaled_values, axis=0)


    def _compute_quadratic(self, quad_values):
        scaled_values = (
            quad_values * self.quad_scale_reciprocals[:, np.newaxis]
        )
        # Like np.outer(...).ravel()
        quad_weights = tf.reshape(self.w * self.w[:, np.newaxis], (-1,))
        return tf.reduce_sum(
            quad_weights[:, tf.newaxis] * scaled_values, axis=0
        )

    def call(self, inputs, linear_values, quad_values):
        """
        Makes the forward pass to map the SM observable to the EFT one.

        Parameters
        ----------
            inputs: number
                This is the SM theoretical prediction that comes after the FK convolution.
            linear_values: dict[str, np.array]
                Dictionary mapping the namses of the linear BSM C-factors for a
                given dataset, to arrays with the cfactor values, whose length
                is the number of datapoints. If not empty, the keys of the
                dictionary must match the ``linear_names`` attribute.
            quad_values: dict[str, np.array]
                Dictionary mapping the namses of the quadratic BSM C-factors for a
                given dataset, to arrays with the cfactor values, whose length is the
                number of datapoints. If not empty, the keys of the
                dictionary must match the ``quad_names`` attribute.


        Returns
        -------
            output: tf.Tensor
               tensor of shape `(ndatapoints, )` with the EFT prediction
        """
        # 1) tensor[:, tf.newaxis] adds an extra dimension to the end of the tensor.
        # 2) tensor_1 * cfactor_values return a tensor of dimensions `(ncfacs, ncfactors)`
        # 3) tf.reduce_sum(tensor, axis=i) sums over the `i` dimension and gets rid of it

        # Convert the BSM factor scales
        # Sort coefficients in canonical order
        if linear_values:
            if (a := set(linear_values)) != (b := set(self.linear_names)):
                raise ValueError(f"BSM factor names don't match {a}, {b}")
            linear_values = np.array(
                [linear_values[k] for k in self.linear_names],
                dtype=np.float32,
            )
            linear = self._compute_linear(linear_values)
        else:
            linear = 0

        if quad_values:
            if (a := set(quad_values)) != (b := set(self.quad_names)):
                raise ValueError(f"BSM quad factor names don't match {a} {b}")
            quad_values = np.array(
                [quad_values[k] for k in self.quad_names],
                dtype=np.float32,
            )
            quadratic = self._compute_quadratic(quad_values)
        else:
            quadratic = 0

        return (1 + linear + quadratic) * inputs
