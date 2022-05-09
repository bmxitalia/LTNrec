from ltnrec.data import MindReaderDataset
from ltnrec.loaders import TrainingDataLoaderLTN, ValDataLoader
from ltnrec.models import LTNTrainerMF, MatrixFactorization
import torch
import numpy as np

torch.manual_seed(11)
np.random.seed(11)

emb_size = [1]
b_size = [64]
lr = [0.001]
lambda_reg = [0.001]
data = MindReaderDataset("./dataset/mr_ntp_all_entities")
val_loader = ValDataLoader(data.validation, 256)
test_loader = ValDataLoader(data.test, 256)
proportions = [0.8, 0.6, 0.4, 0.2]
p_dict = {p: data.get_user_movie_ratings(keep=p) for p in proportions}
torch.manual_seed(11)
np.random.seed(11)
for e in emb_size:
    model = MatrixFactorization(data.n_users, data.n_movies, e, biased=True)
    for l in lr:
        for la in lambda_reg:
            optimizer = torch.optim.Adam(model.parameters(), lr=l, weight_decay=la)
            for b in b_size:
                train_loader = TrainingDataLoaderLTN(p_dict[0.2], b)
                print("Emb size %d - Batch size %d - Lr %.5f" % (e, b, l))
                ltn_rec_mf = LTNTrainerMF(model, optimizer, 0.1)
                ltn_rec_mf.train(train_loader,
                                 val_loader,
                                 "hit@10",
                                 n_epochs=200,
                                 early=20,
                                 verbose=1,
                                 save_path="./ltn.pth")

                ltn_rec_mf.load_model("./ltn.pth")
                test_metrics = ltn_rec_mf.test(test_loader, ["hit@10", "ndcg@10"])
                print("Test metrics: " + str(test_metrics))
