from typing import Any, Dict, List, Optional
import logging
from .base_agent import BaseAgent
import pandas as pd
import numpy as np
from io import StringIO

logger = logging.getLogger(__name__)


class DataAnalysisAgent(BaseAgent):
    """Agent for data analysis tasks"""

    def __init__(self):
        super().__init__(
            name="DataAnalysisAgent",
            description="Analyzes and processes data with pandas",
        )
        self.dataframes = {}
        self.analysis_history = []

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a data analysis task"""
        logger.info(f"Executing analysis task: {task}")

        try:
            result = self._process_analysis(task, **kwargs)
            self.analysis_history.append({"task": task, "result": result})

            return {
                "status": "success",
                "task": task,
                "result": result,
                "total_analyses": len(self.analysis_history),
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {"status": "failed", "task": task, "error": str(e)}

    def _process_analysis(self, task: str, **kwargs) -> Dict[str, Any]:
        """Process the analysis based on task type"""
        task_lower = task.lower()

        if "load" in task_lower or "read" in task_lower:
            return self._load_data(**kwargs)
        elif "statistics" in task_lower or "describe" in task_lower:
            return self._get_statistics(**kwargs)
        elif "filter" in task_lower:
            return self._filter_data(**kwargs)
        elif "aggregate" in task_lower or "group" in task_lower:
            return self._aggregate_data(**kwargs)
        else:
            return {"message": "Analysis task processed", "details": task}

    def _load_data(self, **kwargs) -> Dict[str, Any]:
        """Load data from various sources"""
        source = kwargs.get("source")
        data_name = kwargs.get("name", "default")

        if "csv" in str(source).lower():
            df = pd.read_csv(source)
        elif "json" in str(source).lower():
            df = pd.read_json(source)
        elif isinstance(source, (list, dict)):
            df = pd.DataFrame(source)
        else:
            raise ValueError("Unsupported data source")

        self.dataframes[data_name] = df

        return {
            "name": data_name,
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
        }

    def _get_statistics(self, **kwargs) -> Dict[str, Any]:
        """Get statistical summary of data"""
        data_name = kwargs.get("name", "default")

        if data_name not in self.dataframes:
            raise ValueError(f"Dataset '{data_name}' not found")

        df = self.dataframes[data_name]
        desc = df.describe()

        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "statistics": desc.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
        }

    def _filter_data(self, **kwargs) -> Dict[str, Any]:
        """Filter data based on conditions"""
        data_name = kwargs.get("name", "default")
        condition = kwargs.get("condition")

        if data_name not in self.dataframes:
            raise ValueError(f"Dataset '{data_name}' not found")

        df = self.dataframes[data_name]
        # Store filtered result
        filtered_name = f"{data_name}_filtered"
        self.dataframes[filtered_name] = df.query(condition) if condition else df

        return {
            "original_rows": len(df),
            "filtered_rows": len(self.dataframes[filtered_name]),
            "filtered_name": filtered_name,
        }

    def _aggregate_data(self, **kwargs) -> Dict[str, Any]:
        """Aggregate data by groups"""
        data_name = kwargs.get("name", "default")
        group_by = kwargs.get("group_by")
        agg_func = kwargs.get("agg_func", "mean")

        if data_name not in self.dataframes:
            raise ValueError(f"Dataset '{data_name}' not found")

        df = self.dataframes[data_name]

        if group_by:
            result = df.groupby(group_by).agg(agg_func)
            return {"aggregated_data": result.to_dict(), "groups": group_by}
        else:
            return {"message": "No grouping specified"}

    def get_dataframe(self, name: str = "default") -> Optional[pd.DataFrame]:
        """Get a stored dataframe"""
        return self.dataframes.get(name)

    def list_dataframes(self) -> List[str]:
        """List all stored dataframes"""
        return list(self.dataframes.keys())
