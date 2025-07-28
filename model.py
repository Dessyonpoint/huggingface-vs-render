from huggingface_hub import hf_hub_download
import torch
import torch.nn as nn

# Define the AutoFillEmbeddingNN class
class AutoFillEmbeddingNN(nn.Module):
    def __init__(self, n_service, n_location, n_time, embedding_dim, hidden_size, output_size):
        super(AutoFillEmbeddingNN, self).__init__()
        
        # Embedding layers
        self.service_embedding = nn.Embedding(n_service, embedding_dim)
        self.location_embedding = nn.Embedding(n_location, embedding_dim)
        self.time_embedding = nn.Embedding(n_time, embedding_dim)
        
        # Neural network layers
        input_size = embedding_dim * 3  # 3 embeddings concatenated
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()
        
    def forward(self, service_idx, location_idx, time_idx):
        # Get embeddings
        service_emb = self.service_embedding(service_idx)
        location_emb = self.location_embedding(location_idx)
        time_emb = self.time_embedding(time_idx)
        
        # Concatenate embeddings
        x = torch.cat([service_emb, location_emb, time_emb], dim=-1)
        
        # Forward pass through neural network
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x

# Define same config used during training
n_service = 100
n_location = 50
n_time = 24
embedding_dim = 16
hidden_size = 64
output_size = 10

# Download weights
model_path = hf_hub_download(
    repo_id="desysofly/wakafix-autofill",
    filename="best_wakafix_model.pth"
)

# Reconstruct and load
model = AutoFillEmbeddingNN(n_service, n_location, n_time, embedding_dim, hidden_size, output_size)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()
