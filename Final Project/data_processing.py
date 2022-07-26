import pandas as pd
import numpy as np


def compute_speed(dataframe):
  """Computes the speed of every pedestrian in the dataset using the current and the next positions/frames.

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y

  Returns:
      dataframe: Same datafram as in the input but with the extra SPEED column
  """
  speeds = []
  indexs_cant_compute_velocity = []
  for _, group in dataframe.groupby(by='PedestrianID'):
    # We can't compute the velocity for the last element of each group (pedestrian)
    indexs_cant_compute_velocity.append(group.index[-1])
    for index, row in (list(group.iterrows())[:-1]):
      xy_1 = row[['X', 'Y']].to_numpy()
      xy_2 = dataframe.iloc[index + 1][['X', 'Y']].to_numpy()
      speeds.append(np.linalg.norm(xy_1 - xy_2) * 16) # Frame rate = 16

  # Drop last measurement for each pedestrian, for which we can't compute the velocity
  dataframe.drop(indexs_cant_compute_velocity, inplace=True)

  dataframe = dataframe.reset_index(drop=True)

  # Add velocity
  dataframe['SPEED'] = speeds

  return dataframe

def obtain_neighbors(dataframe):
  """Computes the the neighbors for every pedestrian and every frame in the dataset.

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y, SPEED

  Returns:
      dataframe: Same datafram as in the input but with the extra NEIGHBORS columns
  """
  # Compute neighbors of each pedestrian by frame, because there are frames with more or less pedestrians
  neighbors_positions_per_id_frame = {}
  for _, frame in dataframe.groupby(by='FRAME'):
    pedestrian_ids_frame = set(frame['PedestrianID'])
    for id in pedestrian_ids_frame:
      neighbors_positions = []
      for neighbor_id in pedestrian_ids_frame - set([id]):
        xy_1 = np.squeeze(frame[frame['PedestrianID'] == id][['X', 'Y']].to_numpy())
        xy_2 = np.squeeze(frame[frame['PedestrianID'] == neighbor_id][['X', 'Y']].to_numpy())

        neighbors_positions.append([neighbor_id, xy_2[0], xy_2[1], np.linalg.norm(xy_1 - xy_2)])

      # Sort neighbors information by the distance
      neighbors_positions.sort(key=lambda e: e[3])
      neighbors_positions_per_id_frame[(id, frame.iloc[0]['FRAME'])] = neighbors_positions

  # Add column with neighbors to each pedestrian and frame
  dataframe['NEIGHBORS'] = np.nan
  dataframe['NEIGHBORS'] = dataframe['NEIGHBORS'].astype('object')
  for index, row in dataframe.iterrows():
    dataframe.at[index, 'NEIGHBORS'] = neighbors_positions_per_id_frame[(dataframe.iloc[index]['PedestrianID'], dataframe.iloc[index]['FRAME'])]

  return dataframe

def compute_mean_spacing(dataframe, k):
  """Compute the mean spacing for every pedestrian and frame and the k closest neighbors

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y, SPEED, NEIGHBORS

  Returns:
      dataframe: Same datafram as in the input but with the extra MEAN SPACING column
  """
  # Firstly, delete frames with #pedestrians < k
  frames_to_delete = [] 
  for _, frame in dataframe.groupby(by='FRAME'):
    if len(frame) <= k:
      frames_to_delete.append(frame.iloc[0]['FRAME'])
  dataframe.drop(dataframe[dataframe['FRAME'].isin(frames_to_delete)].index, inplace = True)

  dataframe = dataframe.reset_index(drop = True)

  # Secondly, compute mean spacing
  dataframe['MEAN SPACING'] = np.nan
  for index, row in dataframe.iterrows():
    distances = list(zip(*row['NEIGHBORS']))[3][:k]
    dataframe.at[index, 'MEAN SPACING'] = np.mean(distances)

  return dataframe

def obtain_relative_positions(dataframe, k):
  """Compute the the relative positions for the k closest neighbors for every pedestrian and frame in the dataset

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y, SPEED, NEIGHBORS, MEAN SPACING

  Returns:
      dataframe: Same datafram as in the input but with the extra RELATIVE POSITIONS column
  """
  dataframe['RELATIVE POSITIONS'] = np.nan
  dataframe['RELATIVE POSITIONS'] = dataframe['RELATIVE POSITIONS'].astype('object')
  for index, row in dataframe.iterrows():
    relative_positions = []
    for neighbor in row['NEIGHBORS'][:k]:
      relative_positions.append(np.array([row['X'], row['Y']]) - np.array(neighbor[1:3]))

    dataframe.at[index, 'RELATIVE POSITIONS'] = relative_positions
  
  return dataframe

def preprocess_dataset(dataframe, k):
  """Preprocess the input dataset to obtain a final data with the columns PedestrianID, FRAME, X, Y, SPEED, NEIGHBORS, MEAN SPACING and RELATIVE POSITIONS

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y

  Returns:
      dataframe: Same datafram as in the input but with the extra columns SPEED, NEIGHBORS, MEAN SPACING and RELATIVE POSITIONS
  """
  # Check if we have as input the dataframe or the path to the dataset
  if isinstance(dataframe, str):
    dataframe = pd.read_csv(dataframe,
                            sep=' ',
                            names=['PedestrianID', 'FRAME', 'X', 'Y', 'Z'])

  # Add the speed of each pedestrian
  dataframe = compute_speed(dataframe)

  # Obtain information about neighbors for each pedestrian and frame
  dataframe = obtain_neighbors(dataframe)

  # Compute the mean spacing for each pedestrian sample to k nearest neighbors 
  dataframe = compute_mean_spacing(dataframe, k)

  # Obtain relative positions to k nearest neighbors
  dataframe = obtain_relative_positions(dataframe, k)

  return dataframe

def prepare_data_for_training_testing(dataframe_full, k):
  """Prepares the dataframe with the columns PedestrianID, FRAME, X, Y, SPEED, NEIGHBORS, MEAN SPACING and RELATIVE POSITIONS
  to be consumed by a NN. The final dataset has the columns MEAN SPACING and 2k columns from the flattened RELATIVE POSITION arrays

  Args:
      dataframe (Pandas Dataframe): Dataframe with columns PedestrianID, FRAME, X, Y, SPEED, NEIGHBORS, MEAN SPACING and RELATIVE POSITIONS

  Returns:
      dataframe: Dataframe with the columns MEAN SPACING and 2k columns from the flattened RELATIVE POSITION arrays
  """
  data = pd.DataFrame()

  # Add mean spacing for every pedestrian and frame
  data['MEAN SPACING'] = dataframe_full['MEAN SPACING']

  # Add K closest relative position (flatten)
  positions = np.array([ ("RELATIVE POSITION X {}".format(i), "RELATIVE POSITION Y {}".format(i)) for i in range(k) ]).flatten().tolist()
  relative_positions = pd.DataFrame(columns = positions)
  for index, row in dataframe_full.iterrows():
    new_positions = {}
    x_y = [[X, Y] for (X, Y) in row['RELATIVE POSITIONS'][:k]]
    for index, position in enumerate(np.array(x_y).flatten()):
      new_positions[positions[index]] = position
    relative_positions = relative_positions.append(new_positions, ignore_index=True)

  for column in relative_positions:
    data[column] = relative_positions[column].values

  # Add speed (ground truth)
  data['SPEED'] = dataframe_full['SPEED']

  return data