from tensorflow import function, GradientTape
from tensorflow.keras import Sequential

class CustomTraining(Sequential):
  @function
  def train_step(self, inputs):
      inputs, labels = inputs
      with GradientTape() as tape:
          predictions = self(inputs)
          loss = self.loss(labels, predictions)
      grads = tape.gradient(loss, self.trainable_variables)
      self.optimizer.apply_gradients(zip(grads, self.trainable_variables))
      return {'loss': loss}
