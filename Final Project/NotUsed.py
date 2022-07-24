R_dataset = pd.read_csv('/content/drive/MyDrive/Crowds/data/Corridor_Data/Preprocessed/ug-180-060.csv', converters={'NEIGHBORS': pd.eval})
R_dataset = R_dataset.drop('Unnamed: 0', axis=1)
R_dataset['RELATIVE POSITIONS'] = R_dataset['RELATIVE POSITIONS'].apply(lambda x: pd.eval(re.sub('\)', '', re.sub('array\(', '', x))))
R_dataset = prepare_data_for_training_testing(R_dataset, k, splits)
R_dataset = (R_dataset - R_dataset.min())/(R_dataset.max() - R_dataset.min())

B_dataset = pd.read_csv('/content/drive/MyDrive/Crowds/data/Bottleneck_Data/Preprocessed/uo-180-070.txt', converters={'NEIGHBORS': pd.eval})
B_dataset = B_dataset.drop('Unnamed: 0', axis=1)
B_dataset['RELATIVE POSITIONS'] = B_dataset['RELATIVE POSITIONS'].apply(lambda x: pd.eval(re.sub('\)', '', re.sub('array\(', '', x))))
B_dataset = prepare_data_for_training_testing(B_dataset, k, splits)
B_dataset = (B_dataset - B_dataset.min())/(B_dataset.max() - B_dataset.min())

R_dataset.to_csv('/content/drive/MyDrive/Crowds/data/Corridor_Data/Preprocessed/ug-180-060-normalized.csv')
B_dataset.to_csv('/content/drive/MyDrive/Crowds/data/Bottleneck_Data/Preprocessed/uo-180-070-normalized.csv')



def train_and_evaluate(model_args, kfolds, batch_size, max_epochs, train_validation_split, test_split):
  # Train with K-Fold CV
  models = []
  for fold, (train_idx, valid_idx) in enumerate(kfolds.split(train)):
    train_loader = DataLoader(CrowdDataset(train_validation_split.iloc[train_idx].reset_index(drop=True)), batch_size = batch_size, shuffle = True)
    val_loader = DataLoader(CrowdDataset(train_validation_split.iloc[valid_idx].reset_index(drop=True)), batch_size = batch_size, shuffle = True)

    model = TordeuxNet(model_args)
    trainer = pl.Trainer(max_epochs = max_epochs)#, logger=logger) #logger=tb_logger, early_stop_callback=early_stop_callback, checkpoint_callback=checkpoint_callback
    trainer.fit(model, train_loader, val_loader)

    models.append(model)

  # Compute average CV (last epoch) losses and best model
  avg_training_loss_kcv = 0 
  avg_validation_loss_kcv = 0
  best_model = None
  smallest_validation_loss = np.inf
  for model in models:
    if model.validation_metrics[-1] < smallest_validation_loss:
      best_model = model
      smallest_validation_loss = model.validation_metrics[-1]
    
    avg_training_loss_kcv += float(model.training_metrics[-1])
    avg_validation_loss_kcv += float(model.validation_metrics[-1])

  avg_training_loss_kcv /= len(models)
  avg_validation_loss_kcv /= len(models)

  # choose best model based on test avg loss or last validation epoch???????????????

  # Compute test for best model
  test_loader = DataLoader(CrowdDataset(test_split.reset_index(drop=True)))
  predictor = pl.Trainer(gpus=0)
  test_mse = predictor.predict(best_model, test_loader)
  avg_mse_test = float(torch.stack(test_mse).mean())

  # Prints, plots and returns
  plt.plot(range(len(best_model.training_metrics)), best_model.training_metrics, label = "Training loss")
  plt.plot(range(len(best_model.validation_metrics)), best_model.validation_metrics, label = "Validation loss")
  plt.legend()
  plt.show()

  print("Average training loss of K-Fold CV: {}".format(avg_training_loss_kcv))
  print("Average validation loss of K-Fold CV: {}".format(avg_validation_loss_kcv))
  print("Average MSE for test set: {}".format(avg_mse_test))

  return best_model

best_model = train_and_evaluate(model_args = args, kfolds=kf, batch_size=256, max_epochs=30, train_validation_split=train, test_split=test)