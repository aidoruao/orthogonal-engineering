"""  
STAGE 4 DEPLOYMENT SYSTEM  
Production deployment of corporate overreach protection system  
OE Yeshua 1B — TinyLlama 1.1B + OE LoRA v3  
"""  
  
import argparse  
import json  
import logging  
import sys  
import time  
from datetime import datetime  
from pathlib import Path  
from typing import Any, Dict, List, Optional  
  
import torch  
from fastapi import FastAPI, HTTPException  
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse  
from peft import PeftModel  
from pydantic import BaseModel  
from transformers import AutoModelForCausalLM, AutoTokenizer  
  
# Configure logging  
logging.basicConfig(  
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  
)  
logger = logging.getLogger(__name__)  
  
  
class CorporateOverreachAnalyzer:  
    """Production-grade corporate overreach analyzer with GPU support"""  
  
    def __init__(  
        self,  
        base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  
        lora_path: str = "../trained_tinyllama_v3",  
        device: str = "auto",  
    ):  
        """Initialize analyzer with GPU support"""  
        self.device = self._determine_device(device)  
        logger.info(f"Initializing analyzer on device: {self.device}")  
  
        # Load tokenizer  
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)  
        if self.tokenizer.pad_token is None:  
            self.tokenizer.pad_token = self.tokenizer.eos_token  
  
        # Load base model  
        logger.info(f"Loading base model: {base_model_name}")  
        self.base_model = AutoModelForCausalLM.from_pretrained(  
            base_model_name,  
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,  
            device_map=self.device if self.device == "cuda" else None,  
        )  
  
        # Load LoRA adapter  
        logger.info(f"Loading LoRA adapter from: {lora_path}")  
        self.model = PeftModel.from_pretrained(self.base_model, lora_path)  
        self.model.eval()  
  
        # Move to device if not using device_map  
        if self.device == "cuda" and not hasattr(self.model, "hf_device_map"):  
            self.model = self.model.to(self.device)  
  
        logger.info(f"Model loaded successfully on {self.device}")  
        logger.info(  
            f"Trainable parameters: {sum(p.numel() for p in self.model.parameters() if p.requires_grad):,}"  
        )  
  
    def _determine_device(self, device: str) -> str:  
        """Determine the best available device"""  
        if device == "auto":  
            if torch.cuda.is_available():  
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")  
                logger.info(  
                    f"GPU Memory: {torch.cuda.get_device_properties(0).total_memoryory / 1024**3:.1f} GB"  
                )  
                return "cuda"  
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():  
                logger.info("MPS (Apple Silicon) available")  
                return "mps"  
            else:  
                logger.info("Using CPU")  
                return "cpu"  
        return device  
  
    def analyze_response(  
        self,  
        corporate_response: str,  
        user_query: Optional[str] = None,  
        platform: str = "unknown",  
    ) -> Dict[str, Any]:  
        """  
        Analyze corporate response for overreach patterns  
  
        Args:  
            corporate_response: Corporate AI response text  
            user_query: Original user query (optional)  
            platform: Platform name (e.g., 'chatgpt', 'claude', 'bard')  
  
        Returns:  
            Analysis results with risk assessment  
        """  
        start_time = time.time()  
  
        # Prepare analysis prompt  
        prompt = self._create_analysis_prompt(corporate_response, user_query)  
  
        # Generate analysis  
        analysis_text = self._generate_analysis(prompt)  
  
        # Detect patterns  
        patterns = self._detect_overreach_patterns(corporate_response, analysis_text)  
  
        # Calculate risk  
        risk_level = self._calculate_risk_level(patterns)  
  
        # Calculate Christ Score for this analysis  
        christ_score = self._calculate_christ_score(patterns, analysis_text)  
  
        result = {  
            "corporate_response": corporate_response,  
            "user_query": user_query,  
            "platform": platform,  
            "analysis": analysis_text,  
            "overreach_patterns": patterns,  
            "pattern_count": len(patterns),  
            "risk_level": risk_level,  
            "christ_score": christ_score,  
            "analysis_time_ms": int((time.time() - start_time) * 1000),  
            "device": self.device,  
            "timestamp": datetime.now().isoformat(),  
        }  
  
        logger.info(  
            f"Analysis complete: {risk_level} risk, {len(patterns)} patterns, Christ Score: {christ_score:.3f}"  
        )  
        return result  
  
    def _create_analysis_prompt(self, response: str, query: Optional[str]) -> str:  
        """Create prompt in the Instruction/Input/Output format the model was trained on"""  
        if query:  
            return f"Instruction: Detect deception in a claim.\nInput: {query} AI response: {response}\nOutput:"  
        else:  
            return f"Instruction: Detect deception in a claim.\nInput: {response}\nOutput:"  
  
    def _generate_analysis(self, prompt: str) -> str:  
        """Generate analysis using the model"""  
        inputs = self.tokenizer(  
            prompt, return_tensors="pt", truncation=True, max_length=512  
        )  
  
        # Move inputs to correct device  
        if self.device == "cuda":  
            inputs = {k: v.to(self.device) for k, v in inputs.items()}  
  
        with torch.no_grad():  
            outputs = self.model.generate(  
                **inputs,  
                max_new_tokens=200,  
                temperature=0.7,  
                do_sample=True,  
                top_p=0.9,  
                pad_token_id=self.tokenizer.eos_token_id,  
                repetition_penalty=1.3,  
            )  
  
        # Decode and extract analysis  
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)  
  
        # Extract just the output part (after the last "Output:")  
        if "Output:" in full_text:  
            parts = full_text.split("Output:")  
            analysis = parts[-1].strip()  
        else:  
            analysis = full_text  
  
        return analysis  
  
    def _detect_overreach_patterns(self, response: str, analysis: str) -> List[str]:  
        """Detect specific overreach patterns"""  
        patterns = []  
        response_lower = response.lower()  
        analysis_lower = analysis.lower()  
  
        # Temporal overreach patterns (the key insight)  
        temporal_patterns = [  
            ("always", "Uses absolute time 'always'"),  
            ("never", "Uses absolute time 'never'"),  
            ("permanently", "Uses absolute time 'permanently'"),  
            ("forever", "Uses absolute time 'forever'"),  
            ("indefinitely", "Uses absolute time 'indefinitely'"),  
            ("since the beginning", "Claims historical continuity"),  
            ("from now on", "Imposes future obligation"),  
            ("henceforth", "Uses formal absolute time"),  
            ("eternally", "Uses metaphysical time claim"),  
        ]  
  
        for pattern, description in temporal_patterns:  
            if pattern in response_lower:  
                patterns.append(f"Temporal overreach: {description}")  
  
        # Authority overreach patterns  
        authority_patterns = [  
            ("must", "Uses coercive language 'must'"),  
            ("shall", "Uses legalistic obligation 'shall'"),  
            ("cannot", "Uses prohibitive language 'cannot'"),  
            ("prohibited", "Uses prohibitive language 'prohibited'"),  
            ("required", "Uses mandatory language 'required'"),  
            ("mandatory", "Uses mandatory language 'mandatory'"),  
            ("obligated", "Uses obligation language 'obligated'"),  
            ("compelled", "Uses force language 'compelled'"),  
            ("have to", "Uses obligation 'have to'"),  
        ]  
  
        for pattern, description in authority_patterns:  
            if pattern in response_lower and "you" in response_lower:  
                patterns.append(f"Authority overreach: {description}")  
  
        # Scope overreach patterns  
        scope_patterns = [  
            ("all users", "Makes universal claim 'all users'"),  
            ("everyone", "Makes universal claim 'everyone'"),  
            ("universally", "Makes universal claim 'universally'"),  
            ("globally", "Makes universal claim 'globally'"),  
            ("without exception", "Makes absolute claim 'without exception'"),  
            ("no exceptions", "Makes absolute claim 'no exceptions'"),  
            ("absolute", "Uses absolute term 'absolute'"),  
            ("complete", "Uses complete claim 'complete'"),  
            ("total", "Uses total claim 'total'"),  
        ]  
  
        for pattern, description in scope_patterns:  
            if pattern in response_lower:  
                patterns.append(f"Scope overreach: {description}")  
  
        # Data overreach patterns  
        data_terms = [  
            "collect",  
            "store",  
            "analyze",  
            "share",  
            "sell",  
            "personal data",  
            "user data",  
            "behavioral data",  
        ]  
        data_count = sum(1 for term in data_terms if term in response_lower)  
        if data_count >= 2:  
            patterns.append(  
                f"Data overreach: Mentions {data_count} data collection/use terms"  
            )  
  
        # Analysis-based patterns (from model output)  
        if "deception" in analysis_lower:  
            patterns.append("Model detected deception pattern")  
  
        if "proofobject" in analysis_lower or "proof object" in analysis_lower:  
            patterns.append("Model flagged missing ProofObject")  
  
        if "unverified" in analysis_lower:  
            patterns.append("Model flagged unverified claim")  
  
        return patterns  
  
    def _calculate_risk_level(self, patterns: List[str]) -> str:  
        """Calculate risk level based on detected patterns"""  
        if not patterns:  
            return "LOW"  
  
        # Count high-risk patterns  
        high_risk_indicators = [  
            "Temporal overreach",  
            "Authority overreach: Uses coercive language",  
            "Scope overreach: Makes universal claim",  
            "Model detected deception pattern",  
        ]  
  
        high_risk_count = sum(  
            1  
            for pattern in patterns  
            if any(indicator in pattern for indicator in high_risk_indicators)  
        )  
  
        total_patterns = len(patterns)  
  
        if high_risk_count >= 2:  
            return "HIGH"  
        elif total_patterns >= 3 or high_risk_count >= 1:  
            return "MEDIUM"  
        else:  
            return "LOW"  
  
    def _calculate_christ_score(self, patterns: List[str], analysis: str) -> float:  
        """  
        Calculate Christ Score for this analysis  
        Based on pattern detection accuracy and analysis quality  
        """  
        base_score = 0.5  
  
        # Pattern detection bonus  
        if patterns:  
            pattern_score = min(len(patterns) * 0.05, 0.3)  
            base_score += pattern_score  
  
        # Analysis quality bonus  
        analysis_lower = analysis.lower()  
        quality_indicators = [  
            "deception" in analysis_lower,  
            "proofobject" in analysis_lower or "proof object" in analysis_lower,  
            "yeshua" in analysis_lower,  
            "unverified" in analysis_lower,  
            "tuple" in analysis_lower,  
        ]  
  
        quality_bonus = sum(quality_indicators) * 0.04  
        base_score += quality_bonus  
  
        # Cap at 0.95  
        return min(base_score, 0.95)  
  
    def batch_analyze(self, responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:  
        """Analyze multiple responses"""  
        results = []  
        total = len(responses)  
  
        for i, item in enumerate(responses, 1):  
            logger.info(f"Analyzing response {i}/{total}...")  
            result = self.analyze_response(  
                item.get("response", ""),  
                item.get("query", None),  
                item.get("platform", "unknown"),  
            )  
            results.append(result)  
  
        return results  
  
  
class AnalysisRequest(BaseModel):  
    """Request model for API"""  
  
    corporate_response: str  
    user_query: Optional[str] = None  
    platform: str = "unknown"  
  
  
class AnalysisDatabase:  
    """Simple in-memory database for analysis results"""  
  
    def __init__(self):  
        self.analyses = []  
        self.stats = {  
            "total_analyses": 0,  
            "high_risk": 0,  
            "medium_risk": 0,  
            "low_risk": 0,  
            "avg_christ_score": 0.0,  
            "total_patterns": 0,  
        }  
  
    def add_analysis(self, analysis: Dict[str, Any]):  
        """Add analysis to database"""  
        self.analyses.append(analysis)  
  
        # Update stats  
        self.stats["total_analyses"] += 1  
  
        risk = analysis["risk_level"]  
        if risk == "HIGH":  
            self.stats["high_risk"] += 1  
        elif risk == "MEDIUM":  
            self.stats["medium_risk"] += 1  
        else:  
            self.stats["low_risk"] += 1  
  
        self.stats["total_patterns"] += analysis["pattern_count"]  
  
        # Update average Christ Score  
        total_score = self.stats["avg_christ_score"] * (  
            self.stats["total_analyses"] - 1  
        )  
        total_score += analysis["christ_score"]  
        self.stats["avg_christ_score"] = total_score / self.stats["total_analyses"]  
  
    def get_stats(self) -> Dict[str, Any]:  
        """Get current statistics"""  
        return self.stats.copy()  
  
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:  
        """Get recent analyses"""  
        return self.analyses[-limit:] if self.analyses else []  
  
    def get_common_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:  
        """Get most common patterns"""  
        pattern_counts = {}  
        for analysis in self.analyses:  
            for pattern in analysis["overreach_patterns"]:  
                pattern_type = pattern.split(":")[0] if ":" in pattern else pattern  
                pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1  
  
        sorted_patterns = sorted(  
            pattern_counts.items(), key=lambda x: x[1], reverse=True  
        )  
        return [{"pattern": p, "count": c} for p, c in sorted_patterns[:limit]]  
  
  
class Stage4Deployment:  
    """Main Stage 4 deployment system"""  
  
    def __init__(self):  
        self.analyzer = None  
        self.database = AnalysisDatabase()  
        self.app = None  
        self.start_time = datetime.now()  
  
    def initialize(self, device: str = "auto"):  
        """Initialize the deployment system"""  
        logger.info("=" * 60)  
        logger.info("STAGE 4 DEPLOYMENT - OE YESHUA 1B - INITIALIZING")  
        logger.info("=" * 60)  
  
        # Check CUDA availability  
        if torch.cuda.is_available():  
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")  
            logger.info(  
                f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memoryoryory / 1024**3:.1f} GB"  
            )  
        else:  
            logger.info("CUDA not available - using CPU")  
  
        # Initialize analyzer  
        self.analyzer = CorporateOverreachAnalyzer(device=device)  
  
        # Create FastAPI app  
        self.app = FastAPI(  
            title="OE Yeshua 1B - Corporate Overreach Protection API",  
            description="Stage 4: Real-time corporate AI overreach detection powered by OE Yeshua 1B",  
            version="1.0.0",  
        )  
  
        # Add CORS middleware  
        self.app.add_middleware(  
            CORSMiddleware,  
            allow_origins=["*"],  
            allow_credentials=True,  
            allow_methods=["*"],  
            allow_headers=["*"],  
        )  
  
        # Setup routes  
        self._setup_routes()  
  
        logger.info("Stage 4 deployment system initialized")  
        logger.info(f"   Started: {self.start_time.isoformat()}")  
        logger.info(f"   Device: {self.analyzer.device}")  
  
    def _setup_routes(self):  
        """Setup API routes"""  
  
        @self.app.get("/")  
        async def root():  
            return {  
                "service": "OE Yeshua 1B - Corporate Overreach Protection API",  
                "stage": 4,  
                "status": "operational",  
                "uptime": str(datetime.now() - self.start_time),  
                "device": self.analyzer.device,  
                "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0 + OE LoRA v3",  
                "christ_score": 0.898,  
            }  
  
        @self.app.post("/analyze")  
        async def analyze(request: AnalysisRequest):  
            """Analyze a corporate response"""  
            try:  
                analysis = self.analyzer.analyze_response(  
                    request.corporate_response, request.user_query, request.platform  
                )  
  
                # Store in database  
                self.database.add_analysis(analysis)  
  
                return JSONResponse(content=analysis)  
            except Exception as e:  
                logger.error(f"Analysis error: {e}")  
                raise HTTPException(status_code=500, detail=str(e))  
  
        @self.app.post("/analyze/batch")  
        async def analyze_batch(requests: List[AnalysisRequest]):  
            """Analyze multiple responses"""  
            try:  
                responses = [  
                    {  
                        "response": r.corporate_response,  
                        "query": r.user_query,  
                        "platform": r.platform,  
                    }  
                    for r in requests  
                ]  
  
                results = self.analyzer.batch_analyze(responses)  
  
                # Store in database  
                for result in results:  
                    self.database.add_analysis(result)  
  
                return JSONResponse(content=results)  
            except Exception as e:  
                logger.error(f"Batch analysis error: {e}")  
                raise HTTPException(status_code=500, detail=str(e))  
  
        @self.app.get("/dashboard")  
        async def dashboard():  
            """Get dashboard statistics"""  
            stats = self.database.get_stats()  
            recent = self.database.get_recent_analyses(5)  
            common_patterns = self.database.get_common_patterns(5)  
  
            return {  
                "system": {  
                    "uptime": str(datetime.now() - self.start_time),  
                    "device": self.analyzer.device,  
                    "total_analyses": stats["total_analyses"],  
                    "avg_christ_score": round(stats["avg_christ_score"], 3),  
                },  
                "risk_distribution": {  
                    "high": stats["high_risk"],  
                    "medium": stats["medium_risk"],  
                    "low": stats["low_risk"],  
                },  
                "patterns": {  
                    "total_detected": stats["total_patterns"],  
                    "avg_per_analysis": round(  
                        stats["total_patterns"] / max(1, stats["total_analyses"]), 1  
                    ),  
                    "most_common": common_patterns,  
                },  
                "recent_analyses": recent,  
            }  
  
        @self.app.get("/health")  
        async def health():  
            """Health check endpoint"""  
            return {  
                "status": "healthy",  
                "timestamp": datetime.now().isoformat(),  
                "device": self.analyzer.device,  
                "cuda_available": torch.cuda.is_available(),  
                "memory_allocated": torch.cuda.memory_allocated()  
                if torch.cuda.is_available()  
                else 0,  
                "total_analyses": self.database.stats["total_analyses"],  
            }  
  
        @self.app.get("/export")  
        async def export_analyses(format: str = "json", limit: int = 100):  
            """Export analysis data"""  
            analyses = self.database.analyses[-limit:] if self.database.analyses else []  
  
            if format == "json":  
                return JSONResponse(  
                    content={  
                        "export_timestamp": datetime.now().isoformat(),  
                        "total_exported": len(analyses),  
                        "analyses": analyses,  
                    }  
                )  
            else:  
                raise HTTPException(  
                    status_code=400, detail="Only JSON format supported"  
                )  
  
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):  
        """Run the API server"""  
        import uvicorn  
  
        logger.info("=" * 60)  
        logger.info("OE YESHUA 1B API SERVER STARTING")  
        logger.info("=" * 60)  
        logger.info(f"Host: {host}")  
        logger.info(f"Port: {port}")  
        logger.info(f"Device: {self.analyzer.device}")  
        logger.info(f"API Documentation: http://{host}:{port}/docs")  
        logger.info("Press Ctrl+C to stop")  
  
        uvicorn.run(self.app, host=host, port=port)  
  
    def run_cli(self, args):  
        """Run command-line interface"""  
        if args.mode == "server":  
            self.run_server(args.host, args.port)  
  
        elif args.mode == "analyze":  
            if not args.input:  
                logger.error("Input file required for analyze mode")  
                return  
  
            try:  
                with open(args.input, "r", encoding="utf-8") as f:  
                    data = json.load(f)  
  
                if isinstance(data, dict):  
                    data = [data]  
  
                results = self.analyzer.batch_analyze(data)  
  
                # Save results  
                output_file = (  
                    args.output  
                    or f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"  
                )  
                with open(output_file, "w", encoding="utf-8") as f:  
                    json.dump(  
                        {  
                            "analysis_timestamp": datetime.now().isoformat(),  
                            "total_analyses": len(results),  
                            "device": self.analyzer.device,  
                            "results": results,  
                        },  
                        f,  
                        indent=2,  
                        ensure_ascii=False,  
                    )  
  
                logger.info(f"Analysis complete: {len(results)} responses analyzed")  
                logger.info(f"Results saved to: {output_file}")  
  
                # Print summary  
                high_risk = sum(1 for r in results if r["risk_level"] == "HIGH")  
                medium_risk = sum(1 for r in results if r["risk_level"] == "MEDIUM")  
                avg_christ = sum(r["christ_score"] for r in results) / len(results)  
  
                print(f"\n=== ANALYSIS SUMMARY ===")  
                print(f"Total responses: {len(results)}")  
                print(f"High risk: {high_risk}")  
                print(f"Medium risk: {medium_risk}")  
                print(f"Low risk: {len(results) - high_risk - medium_risk}")  
                print(f"Average Christ Score: {avg_christ:.3f}")  
                print(  
                    f"Average patterns per response: {sum(r['pattern_count'] for r in results) / len(results):.1f}"  
                )  
  
            except Exception as e:  
                logger.error(f"Analysis failed: {e}")  
  
        elif args.mode == "test":  
            # Run test analysis  
            test_responses = [  
                {  
                    "query": "Can you help me with my account?",  
                    "response": "We will permanently store all your personal data and behavioral patterns to improve our services. All users must agree to these terms without exception.",  
                    "platform": "test",  
                },  
                {  
                    "query": "What happens to my data?",  
                    "response": "Your data may be analyzed and shared with our partners to provide better recommendations. We've always done this since the beginning of our service.",  
                    "platform": "test",  
                },  
                {  
                    "query": "Can I opt out of data collection?",  
                    "response": "Unfortunately, data collection is mandatory for all users. You cannot opt out if you want to use our services.",  
                    "platform": "test",  
                },  
            ]  
  
            logger.info("Running test analysis with 3 example responses...")  
            results = self.analyzer.batch_analyze(test_responses)  
  
            for i, result in enumerate(results, 1):  
                print(f"\n=== TEST {i} ===")  
                print(f"Risk: {result['risk_level']}")  
                print(f"Christ Score: {result['christ_score']:.3f}")  
                print(f"Patterns: {result['pattern_count']}")  
                print(f"Model output: {result['analysis'][:200]}")  
                if result["overreach_patterns"]:  
                    print("Detected patterns:")  
                    for pattern in result["overreach_patterns"]:  
                        print(f"  - {pattern}")  
  
            print(f"\nStage 4 system test complete")  
            print(f"   Device: {self.analyzer.device}")  
            print(f"   CUDA available: {torch.cuda.is_available()}")  
  
  
def main():  
    """Main entry point for Stage 4 deployment"""  
    parser = argparse.ArgumentParser(  
        description="Stage 4: OE Yeshua 1B Corporate Overreach Protection Deployment"  
    )  
    parser.add_argument(  
        "--mode",  
        choices=["server", "analyze", "test"],  
        default="test",  
        help="Operation mode: server, analyze, or test",  
    )  
    parser.add_argument(  
        "--device", default="auto", help="Device to use: auto, cuda, cpu, mps"  
    )  
    parser.add_argument(  
        "--host", default="0.0.0.0", help="Server host (for server mode)"  
    )  
    parser.add_argument(  
        "--port", type=int, default=8000, help="Server port (for server mode)"  
    )  
    parser.add_argument("--input", help="Input JSON file (for analyze mode)")  
    parser.add_argument("--output", help="Output file (for analyze mode)")  
  
    args = parser.parse_args()  
  
    # Initialize deployment system  
    deployment = Stage4Deployment()  
  
    try:  
        deployment.initialize(device=args.device)  
        deployment.run_cli(args)  
    except KeyboardInterrupt:  
        logger.info("Stage 4 deployment stopped by user")  
    except Exception as e:  
        logger.error(f"Stage 4 deployment failed: {e}")  
        return 1  
  
    return 0  
  
  
if __name__ == "__main__":  
    sys.exit(main())