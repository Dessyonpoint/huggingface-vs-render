from huggingface_hub import hf_hub_download
import torch

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
