import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import Dataset
import pytorch_lightning as pl

class TordeuxNet(pl.LightningModule):
  def __init__(self, args):
    super().__init__()
    self.net = nn.Sequential(
        nn.Linear(1 + 2 * args["k"], 3),
        nn.ReLU(), 
        nn.Linear(3,3),
        nn.ReLU(),
        nn.Linear(3, 1),
    )
    self.lr = args['lr']
    self.loss = F.mse_loss

    self.training_metrics = []
    self.validation_metrics = []

  def forward(self, x):
    speed = self.net(x)
    return speed

  def configure_optimizers(self):
    # The paper uses the implementation from neuralnet R package. 
    # It uses Backpropagation (Rumelhart 1986) without specific LR. 
    # The most similar algorithm in PyTorch is SGD, but we use Adam.
    optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
    return optimizer

  def training_step(self, train_batch, batch_idx):
    x, y = train_batch
    x_hat = self.net(x.float())
    loss = self.loss(x_hat, y.float().unsqueeze(1))

    self.log('train_loss', loss)

    return {"loss": loss}

  def validation_step(self, val_batch, batch_idx):
    x, y = val_batch
    x_hat = self.net(x.float())
    loss = self.loss(x_hat, y.float().unsqueeze(1))

    self.log("val_loss", loss)

    return {"loss": loss}

  def predict_step(self, batch, batch_idx):
    x, y = batch
    x_hat = self(x.float())
    mse = self.loss(x_hat, y.float().unsqueeze(1))

    return mse

  def training_epoch_end(self, outputs):
    avg_loss = torch.stack([x['loss'] for x in outputs]).mean()

    self.training_metrics.append(avg_loss)

    return None

  def validation_epoch_end(self, outputs):
    avg_loss = torch.stack([x['loss'] for x in outputs]).mean()

    self.validation_metrics.append(avg_loss)

    return None

class CrowdDataset(Dataset):
  def __init__(self, dataframe):
    self.x_train=torch.tensor(dataframe.loc[:, dataframe.columns != 'SPEED'].values)

    self.y_train=torch.tensor(dataframe['SPEED'].values)
 
  def __len__(self):
    return len(self.y_train)
   
  def __getitem__(self,idx):
    return self.x_train[idx], self.y_train[idx]