"""Conselho de veto para segurança"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VetoCouncil:
    """Conselho multisig com poder de veto"""
    
    def __init__(self, council_members: List[str], required_signatures: int):
        """
        Inicializa conselho de veto
        
        Args:
            council_members: Lista de endereços dos membros
            required_signatures: Número mínimo de assinaturas para veto
        """
        self.council_members = council_members
        self.required_signatures = required_signatures
        self.logger = logger
        self.active_vetoes: Dict[str, Dict] = {}
    
    def propose_veto(self, proposer: str, proposal_id: str, reason: str) -> bool:
        """Propõe um veto a uma proposta"""
        try:
            if proposer not in self.council_members:
                raise ValueError("Proposer não é membro do conselho")
            
            if proposal_id in self.active_vetoes:
                raise ValueError(f"Veto já existe para {proposal_id}")
            
            self.active_vetoes[proposal_id] = {
                'proposer': proposer,
                'reason': reason,
                'signatures': [],  # ORA 20/07/2026: proponente NAO conta como assinatura propria -- corrigido bug real de quorum (2-de-3 aprovava com so 1 assinatura externa)
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            self.logger.info(f"Veto proposto: {proposal_id} por {proposer}")
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao propor veto: {e}")
            raise
    
    def sign_veto(self, signer: str, proposal_id: str) -> bool:
        """Membro do conselho assina veto"""
        try:
            if signer not in self.council_members:
                raise ValueError("Signatário não é membro do conselho")
            
            if proposal_id not in self.active_vetoes:
                raise ValueError(f"Veto {proposal_id} não existe")
            
            veto = self.active_vetoes[proposal_id]
            
            if signer in veto['signatures']:
                raise ValueError("Signatário já assinou este veto")
            
            veto['signatures'].append(signer)
            
            # Verificar se atingiu quórum
            if len(veto['signatures']) >= self.required_signatures:
                veto['status'] = 'approved'
                self.logger.info(f"Veto {proposal_id} APROVADO (quórum atingido)")
                return True
            
            self.logger.info(f"Veto {proposal_id}: {len(veto['signatures'])}/{self.required_signatures} assinaturas")
            return False
        
        except Exception as e:
            self.logger.error(f"Erro ao assinar veto: {e}")
            raise
    
    def is_vetoed(self, proposal_id: str) -> bool:
        """Verifica se proposta foi vetada"""
        if proposal_id not in self.active_vetoes:
            return False
        return self.active_vetoes[proposal_id]['status'] == 'approved'
    
    def get_veto_status(self, proposal_id: str) -> Optional[Dict]:
        """Retorna status de um veto"""
        return self.active_vetoes.get(proposal_id)
