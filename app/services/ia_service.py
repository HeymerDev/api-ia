import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IAService:
    def __init__(self, config):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🎮 Dispositivo: {self.device.upper()}")
    
    def load_model(self):
        try:
            logger.info("🤖 Cargando modelo base...")
            
            # Cargar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.MODEL_BASE_PATH)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            logger.info("✅ Tokenizer cargado")
            
            # Cargar modelo base
            base_model = AutoModelForCausalLM.from_pretrained(
                self.config.MODEL_BASE_PATH,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            logger.info("✅ Modelo base cargado")
            
            # Cargar adaptadores LoRA
            logger.info("🔧 Cargando adaptadores LoRA...")
            self.model = PeftModel.from_pretrained(base_model, self.config.LORA_PATH)
            
            # Fusionar adaptadores
            logger.info("⚡ Fusionando adaptadores...")
            self.model = self.model.merge_and_unload()
            
            self.model.eval()
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("✅ Modelo con LoRA cargado y listo")
            logger.info(f"📊 Parámetros: {self.model.num_parameters():,}")
            
        except Exception as e:
            logger.error(f"❌ Error al cargar modelo: {e}")
            raise
    
    def generar_respuesta(
        self, 
        pregunta: str,
        contexto: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generar respuesta usando el modelo"""
        
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Modelo no cargado")
        
        max_tokens = max_tokens or self.config.MAX_TOKENS
        temperature = temperature or self.config.TEMPERATURE
        
        prompt = self._construir_prompt(pregunta, contexto)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=self.config.TOP_P,
                top_k=50,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
            )
        
        texto_completo = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        respuesta = self._extraer_respuesta(texto_completo)
        
        return respuesta
    
    def _construir_prompt(self, pregunta: str, contexto: Optional[Dict[str, Any]] = None) -> str:
        """Construir prompt con formato adecuado"""
        
        instruccion = """Eres el asistente académico oficial de la Corporación Universitaria Latinoamericana (CUL). 
Gestionas tutorías, docentes y seguimiento académico.
Respondes de forma clara, profesional y amigable."""
        
        contexto_str = ""
        if contexto:
            contexto_str = "\n\n### Información disponible:\n"
            
            if "docentes" in contexto and contexto["docentes"]:
                contexto_str += "Docentes: " + ", ".join([
                    f"{d.get('nombre', '')} {d.get('apellido', '')} ({d.get('especialidad', '')})"
                    for d in contexto["docentes"]
                ]) + "\n"
            
            if "materias" in contexto and contexto["materias"]:
                contexto_str += "Materias: " + ", ".join([
                    m.get('nombre', '') for m in contexto["materias"]
                ]) + "\n"
            
            if "estudiante" in contexto:
                est = contexto["estudiante"]
                contexto_str += f"Estudiante: {est.get('nombre', '')} ({est.get('codigo_estudiante', '')})\n"
            
            if "tutorias" in contexto and contexto["tutorias"]:
                contexto_str += f"Tutorías programadas: {len(contexto['tutorias'])}\n"
            
            if "seguimiento" in contexto and contexto["seguimiento"]:
                contexto_str += f"Registros de seguimiento: {len(contexto['seguimiento'])}\n"
        
        prompt = f"""### Instrucción:
{instruccion}
{contexto_str}
### Entrada:
{pregunta}

### Respuesta:
"""
        
        return prompt
    
    def _extraer_respuesta(self, texto_completo: str) -> str:
        """Extraer solo la respuesta del modelo"""
        
        if "### Respuesta:" in texto_completo:
            partes = texto_completo.split("### Respuesta:")
            respuesta = partes[-1].strip()
            
            if "###" in respuesta:
                respuesta = respuesta.split("###")[0].strip()
            
            return respuesta
        
        return texto_completo.strip()
    
    def detectar_intencion(self, texto: str) -> str:
        """Detectar la intención del usuario"""
        texto_lower = texto.lower()
        
        if any(word in texto_lower for word in ['hola', 'buenos días', 'buenas tardes', 'hey']):
            return 'saludo'
        
        if any(word in texto_lower for word in ['profesor', 'docente', 'maestro', 'quien dicta']):
            return 'consultar_docentes'
        
        if any(word in texto_lower for word in ['registr', 'agendar', 'programar', 'tutoria', 'tutoría']):
            return 'registrar_tutoria'
        
        if any(word in texto_lower for word in ['avance', 'progreso', 'cómo va', 'rendimiento', 'seguimiento']):
            return 'consultar_avance'
        
        if any(word in texto_lower for word in ['asign', 'asociar']):
            return 'asignar_estudiante'
        
        return 'consulta_general'

# Instancia global
ia_service = None

def init_ia_service(config):
    """Inicializar servicio de IA"""
    global ia_service
    ia_service = IAService(config)
    ia_service.load_model()
    return ia_service

def get_ia_service():
    """Obtener instancia del servicio de IA"""
    if ia_service is None:
        raise RuntimeError("Servicio de IA no inicializado")
    return ia_service