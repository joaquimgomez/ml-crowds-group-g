from NeuralNetwork import TordeuxNet, CrowdDataset

import torch
from sklearn.model_selection import KFold, train_test_split
from torch.utils.data import DataLoader
import pytorch_lightning as pl
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import TQDMProgressBar

import numpy as np

import matplotlib.pyplot as plt

def simple_train(model_args, batch_size, max_epochs, dataset):
  train, remain = train_test_split(dataset, train_size=0.8)
  validation, test = train_test_split(remain, test_size = 0.5)

  train_loader = DataLoader(CrowdDataset(train.reset_index(drop=True)), batch_size = batch_size, shuffle = True)
  val_loader = DataLoader(CrowdDataset(validation.reset_index(drop=True)), batch_size = batch_size, shuffle = False)
  test_loader = DataLoader(CrowdDataset(test.reset_index(drop=True)), shuffle = False)

  # Train model
  model = TordeuxNet(model_args)
  trainer = pl.Trainer(accelerator="gpu", devices=1, max_epochs = max_epochs, callbacks=[EarlyStopping(monitor="val_loss", mode="min", patience=10)])
  trainer.fit(model, train_loader, val_loader)

  # Compute test MSE
  test_mse = trainer.predict(model, test_loader)

  # Prints, plots and returns
  plt.plot(range(len(model.training_metrics)), model.training_metrics, label = "Training loss")
  plt.plot(range(len(model.validation_metrics)), model.validation_metrics, label = "Validation loss")
  plt.legend()
  plt.show()

  print("Last epoch training loss: {}".format(model.training_metrics[-1]))
  print("Last epoch validation loss: {}".format(model.validation_metrics[-1]))
  print("Test MSE: {}".format(float(torch.stack(test_mse).mean())))

  return model.training_metrics[-1], model.training_metrics[-1], float(torch.stack(test_mse).mean())

def train_and_evaluate(model_args, kfolds, batch_size, max_epochs, train_validation_split, test_split):
  kf = KFold(n_splits=kfolds, random_state=1234, shuffle=True)

  # Train with K-Fold CV and save losses
  cv_training_losses = []
  cv_validation_losses = []
  cv_test_losses = []
  for fold, (train_idx, valid_idx) in enumerate(kf.split(train_validation_split)):
    print("CV ITERATION {}".format(fold))
    train_loader = DataLoader(CrowdDataset(train_validation_split.iloc[train_idx].reset_index(drop=True)), batch_size = batch_size, shuffle = True, num_workers = 2)
    val_loader = DataLoader(CrowdDataset(train_validation_split.iloc[valid_idx].reset_index(drop=True)), batch_size = batch_size, shuffle = True, num_workers = 2)
    test_loader = DataLoader(CrowdDataset(test_split.reset_index(drop=True)), num_workers = 2)

    # Train model
    model = TordeuxNet(model_args)
    trainer = pl.Trainer(accelerator="gpu", devices=1, max_epochs = max_epochs, callbacks=[EarlyStopping(monitor="val_loss", mode="min", patience=10), TQDMProgressBar(refresh_rate=15)])
    trainer.fit(model, train_loader, val_loader)

    # Save training and validation losses
    cv_training_losses.append(float(model.training_metrics[-1]))
    cv_validation_losses.append(float(model.validation_metrics[-1]))

    # Compute and save test losses
    test_mse = trainer.predict(model, test_loader)
    cv_test_losses.append(float(torch.stack(test_mse).mean()))

  return cv_training_losses, cv_validation_losses, cv_test_losses

def bootstrap_cv(dataset, bootstrapping_iterations, bootstrapping_num_samples, model_args, folds, batch_size, max_epochs, diff_test_dataset = None):
  bootstrap_training_losses = []
  bootstrap_validation_losses = []
  bootstrap_test_losses = []
  for i in range(0, bootstrapping_iterations):
    print("BOOTSTRAP ITERATION {}".format(i))
    # Select random for bootstrapping iteration at random
    bootstrap_data = dataset.sample(n = bootstrapping_num_samples)

    # Half of the data for training, half for testing
    if diff_test_dataset is not None:
      train = dataset.sample(n=int(bootstrapping_num_samples / 2))
      test = diff_test_dataset.sample(n=int(bootstrapping_num_samples / 2))
    else:
      train, test = train_test_split(bootstrap_data, test_size=0.5)

    # Cross-validation
    train_losses, validation_losses, test_losses = train_and_evaluate(model_args, folds, batch_size, max_epochs, train, test)

    bootstrap_training_losses.append(np.mean(train_losses))
    bootstrap_validation_losses.append(np.mean(validation_losses))
    bootstrap_test_losses.append(np.mean(test_losses))

  # Print results
  print("Train mean: {} -- Train STD; {}".format(np.mean(np.array(bootstrap_training_losses)), np.std(np.array(bootstrap_training_losses))))
  print("Validation mean: {} -- Validation STD: {}".format(np.mean(np.array(bootstrap_validation_losses)), np.std(np.array(bootstrap_validation_losses))))
  print("Test mean: {} -- Test STD: {}".format(np.mean(np.array(bootstrap_test_losses)), np.std(np.array(bootstrap_test_losses))))