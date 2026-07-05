from pathlib import Path
import json

class ExperimentLogger:
    def __init__(self, output_dir='results'):
        self.output_dir=Path(output_dir)
        self.output_dir.mkdir(parents=True,exist_ok=True)

    def save_metrics(self,name,metrics):
        with open(self.output_dir/f'{name}.json','w') as f:
            json.dump(metrics,f,indent=2)
