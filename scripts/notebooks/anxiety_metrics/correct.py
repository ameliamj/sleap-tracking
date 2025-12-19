import sys
sys.path.append('../../../')

from src.classes.pred_loader import PredLoader

preds = PredLoader('large_arena' + '_preds_df.csv')

# preds.get_nan()
preds.correct()
