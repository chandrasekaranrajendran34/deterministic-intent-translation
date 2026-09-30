from pathlib import Path
import matplotlib.pyplot as plt
def make_plots(m,conf,out):
 out=Path(out); out.mkdir(parents=True,exist_ok=True)
 for col in ["accept_reject_accuracy","invalid_rejection_f1","service_type_accuracy","schema_validity_rate","hallucination_rate","descriptor_success_rate","mean_latency_ms"]:
  fig,ax=plt.subplots(figsize=(5.2,3.2)); ax.bar(m.pipeline,m[col]); ax.set_xlabel("Pipeline"); ax.set_ylabel(col.replace("_"," ").title()); fig.tight_layout(); fig.savefig(out/f"{col}.pdf"); fig.savefig(out/f"{col}.png",dpi=300); plt.close(fig)
 for name,cm in conf.items():
  fig,ax=plt.subplots(figsize=(4,3.5)); ax.imshow(cm)
  for i in range(2):
   for j in range(2): ax.text(j,i,str(cm[i,j]),ha="center",va="center")
  ax.set_xticks([0,1],["Rejected","Accepted"]); ax.set_yticks([0,1],["Invalid","Valid"]); ax.set_xlabel("Predicted"); ax.set_ylabel("Expected"); fig.tight_layout(); fig.savefig(out/f"confusion_{name}.pdf"); plt.close(fig)