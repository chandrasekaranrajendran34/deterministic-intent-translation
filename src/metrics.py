import pandas as pd
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
def summarize(df):
 a=[]
 for p,g in df.groupby("pipeline",sort=False):
  y=g.expected_valid.astype(bool); q=g.accepted.astype(bool); inv=(~y).astype(int); rej=(~q).astype(int); mask=g.expected_service.notna()
  a.append({"pipeline":p,"n":len(g),"accept_reject_accuracy":accuracy_score(y,q),"invalid_rejection_precision":precision_score(inv,rej,zero_division=0),"invalid_rejection_recall":recall_score(inv,rej,zero_division=0),"invalid_rejection_f1":f1_score(inv,rej,zero_division=0),"service_type_accuracy":(g.loc[mask,"expected_service"]==g.loc[mask,"predicted_service"]).mean(),"schema_validity_rate":g.schema_valid.mean(),"hallucination_rate":g.hallucination_detected.mean(),"descriptor_success_rate":g.descriptor_success.mean(),"mean_latency_ms":g.latency_ms.mean(),"p95_latency_ms":g.latency_ms.quantile(.95)})
 return pd.DataFrame(a)
def confusions(df): return {p:confusion_matrix(g.expected_valid.astype(int),g.accepted.astype(int),labels=[0,1]) for p,g in df.groupby("pipeline")}