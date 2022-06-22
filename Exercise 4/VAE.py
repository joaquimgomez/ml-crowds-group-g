from gc import callbacks
from tensorflow import keras
from keras.models import Model
from keras import Input
from keras.layers import Dense, Lambda
import tensorflow as tf
from keras import backend as K

import numpy as np

#import graphviz # for showing model diagram
import matplotlib.pyplot as plt
import plotly.express as px


def sampling(args):
    """Function used to randomly sample from the latent space distribution.
    Note, epsilon is sampled from a standard normal distribution and is used to maintain the required stochasticity of Z.
    Meanwhile, z-mean and z-sigma remain deterministic allowing the loss to backpropagate through the layers.

    Args:
        args (list): List of arguments required by the normal distribution.

    Returns:
        float: Result of the smapling from the standard Normal.
    """

    z_mean, z_log_sigma, latent_dim = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], latent_dim), mean=0., stddev=1.)
    return z_mean + K.exp(z_log_sigma) * epsilon

def create_encoder(original_dim, latent_dim):
    """Creates and returns a keras model consisting of an encoder with orginal_dim input size
    and a latent space dimension of latent_dim.

    Args:
        original_dim (int): Input layer dimension.
        latent_dim (int): Latent dimension.

    Returns:
        keras.Model: Encoder model.
        keras.Input: Input layer of the model.
    """
    # Input Layer 
    visible = keras.Input(shape=(original_dim,), name='Encoder-Input-Layer')

    # Hidden Layer
    h_enc1 = Dense(units=256, activation='relu', name='Encoder-Hidden-Layer-1')(visible)
    h_enc2 = Dense(units=256, activation='relu', name='Encoder-Hidden-Layer-2')(h_enc1)

    # Custom Latent Space Layer
    z_mean = Dense(units=latent_dim, name='Z-Mean')(h_enc2) # Mean component
    z_log_sigma = Dense(units=latent_dim, name='Z-Log-Sigma')(h_enc2) # Standard deviation component
    z = Lambda(sampling, name='Z-Sampling-Layer')([z_mean, z_log_sigma, latent_dim]) # Z sampling layer

    # Create Encoder model
    encoder = Model(visible, [z_mean, z_log_sigma, z], name='Encoder-Model')

    return encoder, visible

def create_decoder(latent_dim, original_dim):
    """Creates and returns a keras model consisting of a decoder with latent_dim input size
    and original_dim as output dimension.

    Args:
        latent_dim (int): Input layer dimension.
        original_dim (int): Output layer dimension.
        
    Returns:
        keras.Model: Decoder model.
    """
    # Input Layer 
    latent_inputs = Input(shape=(latent_dim,), name='Input-Z-Sampling')

    # Hidden Layer
    h_dec = Dense(units=256, activation='relu', name='Decoder-Hidden-Layer-1')(latent_inputs)
    h_dec2 = Dense(units=256, activation='relu', name='Decoder-Hidden-Layer-2')(h_dec)

    # Output Layer
    outputs = Dense(original_dim, activation='relu', name='Decoder-Output-Layer')(h_dec2)

    # Create Decoder model
    decoder = Model(latent_inputs, outputs, name='Decoder-Model')

    return decoder

def create_vae(encoder, decoder, visible, original_dim):
    """Creates and returns a keras model consisting of a Variational Auto-Encoder.

    Args:
        encoder (keras.Model): Encoder model.
        decoder (keras.Model): Decoder model.
        visible (keras.input): Input layer of the encoder.
        original_dim (int): Dimension of the input layer of the Encoder.
        
    Returns:
        keras.Model: VAE model.
        keras.Model: Encoder model.
        keras.Model: Decoder model.
    """
    # Outputs available from encoder model are z_mean, z_log_sigma and z
    z_mean = encoder(visible)[0]
    z_log_sigma = encoder(visible)[1]
    z = encoder(visible)[2]

    # Define outputs from a VAE model by specifying how the encoder-decoder models are linked
    output = decoder(z)
    
    # Instantiate a VAE model
    vae = Model(inputs=visible, outputs=output, name='VAE-Model')

    # Add losses
    # 1. Reconstruction loss compares inputs and outputs and tries to minimise the difference
    r_loss = original_dim * keras.losses.mse(visible, output)  # use MSE

    # 2. KL divergence loss compares the encoded latent distribution Z with standard Normal distribution and penalizes if it's too different
    kl_loss =  -0.5 * K.sum(1 + z_log_sigma - K.square(z_mean) - K.exp(z_log_sigma), axis = 1)

    # The VAE loss is a combination of reconstruction loss and KL loss
    vae_loss = K.mean(r_loss + kl_loss)

    # Add loss to the model and compile it
    vae.add_loss(vae_loss)

    # vae.compile(optimizer='adam')
    vae.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))

    return vae, encoder, decoder

def train_and_plot_vae(vae, encoder, decoder, X_train, X_test, epochs=100, batch_size=128, callbacks=[]):
    """Given a VAE model, trains the model and plots the loss per epoch.

    Args:
        vae (keras.Model): VAE model.
        encoder (keras.Model): Encoder model.
        decoder (keras.Model): Decoder model.
        X_train (array): Training data.
        X_test (array): Test data.
        epochs (int): Number of training epochs.
        batch_size (int): Batch size.
        callbacks (list): List of trainign callbacks.
        
    Returns:
        keras.Model: VAE model.
        keras.Model: Encoder model.
        keras.Model: Decoder model.
    """
    # Train VAE model
    history = vae.fit(X_train, X_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, X_test), callbacks=callbacks)

    # Plot a loss chart
    fig, ax = plt.subplots(figsize=(16,9), dpi=300)
    plt.title(label='Model Loss by Epoch', loc='center')

    ax.plot(history.history['loss'], label='Training Data', color='black')
    ax.plot(history.history['val_loss'], label='Test Data', color='red')
    ax.set(xlabel='Epoch', ylabel='Loss')
    plt.xticks(ticks=np.arange(len(history.history['loss']), step=1), labels=np.arange(1, len(history.history['loss'])+1, step=1))
    plt.legend()
    plt.show()

    return vae, encoder, decoder

def visualize_latent_space(encoder, X_test, y_test):
    # Use encoder model to encode inputs into a latent space
    X_test_encoded = encoder.predict(X_test)

    # Recall that our encoder returns 3 arrays: z-mean, z-log-sigma and z. We plot the values for z
    # Create a scatter plot
    fig = px.scatter(None, x=X_test_encoded[2][:,0], y=X_test_encoded[2][:,1], 
                    opacity=1, color=y_test.astype(str))

    # Change chart background color
    fig.update_layout(dict(plot_bgcolor = 'white'))

    # Update axes lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='white', 
                    zeroline=True, zerolinewidth=1, zerolinecolor='white', 
                    showline=True, linewidth=1, linecolor='white',
                    title_font=dict(size=10), tickfont=dict(size=10))

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='white', 
                    zeroline=True, zerolinewidth=1, zerolinecolor='white', 
                    showline=True, linewidth=1, linecolor='white',
                    title_font=dict(size=10), tickfont=dict(size=10))

    # Set figure title
    fig.update_layout(title_text="MNIST digit representation in the 2D Latent Space")

    # Update marker size
    fig.update_traces(marker=dict(size=2))

    fig.show()

def reconstruct_digits(X_test, encoder, decoder):
    """Given an enconder and a decoder reconstruct the X_test data and plots the original and the reconstructed versions.

    Args:
        encoder (keras.Model): Encoder model.
        decoder (keras.Model): Decoder model.
        X_test (array): Test data.
    """
    x_sample = X_test
    x_e = encoder.predict(X_test)
    x_d = decoder.predict(x_e[2])
    x_reconstruct = x_d

    plt.figure(figsize=(8, 36))
    for i in range(15):
        plt.subplot(15, 2, 2*i + 1)
        plt.imshow(x_sample[i].reshape(28, 28), vmin=0, vmax=1, cmap="gray")
        plt.title("Original Digit")
        plt.colorbar()
        plt.subplot(15, 2, 2*i + 2)
        plt.imshow(x_reconstruct[i].reshape(28, 28), vmin=0, vmax=1, cmap="gray")
        plt.title("Reconstructed Digit")
        plt.colorbar()
    plt.tight_layout()

def generate_digits(decoder):
    """Given a decoder generates 15 digits.

    Args:
        decoder (keras.Model): Decoder model.
    """
    image_size = 28
    values = np.arange(-3, 4, .5)
    xx, yy = np.meshgrid(values, values)
    input_holder = np.zeros((1, 2))

    # Matrix that will contain the grid of images
    container = np.zeros((image_size * len(values), image_size * len(values)))

    for row in range(8):
        for col in range(2):
            input_holder = np.array([[xx[row, col], yy[row, col]]])
            output = decoder.predict(input_holder)
            artificial_image = output.reshape((image_size,image_size))
            container[row * image_size: (row + 1) * image_size, col * image_size: (col + 1) * image_size] = np.squeeze(artificial_image)
        
    plt.figure(figsize=(50,7))
    plt.xlim(50)
    plt.ylim(250)
    plt.imshow(container, cmap='gray')
