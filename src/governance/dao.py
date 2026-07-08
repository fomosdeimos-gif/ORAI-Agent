"""Sistema DAO para governance do ORA"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ProposalStatus(Enum):
    """Estados de uma proposta"""
    PENDING = "pending"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

@dataclass
class Proposal:
    """Proposta de governance"""
    id: str
    title: str
    description: str
    proposer: str
    proposal_type: str  # "strategy_change", "parameter_update", "emergency_pause"
    target_parameter: Optional[str]
    new_value: Optional[str]
    voting_start: datetime
    voting_end: datetime
    status: ProposalStatus
    votes_for: int
    votes_against: int
    votes_abstain: int
    execution_timestamp: Optional[datetime] = None

class GovernanceDAO:
    """DAO para governance do ORA"""
    
    def __init__(self, governance_token_holders: Dict[str, float]):
        """
        Inicializa DAO
        
        Args:
            governance_token_holders: Dicionário de holders e seus saldos de tokens
        """
        self.token_holders = governance_token_holders
        self.proposals: Dict[str, Proposal] = {}
        self.user_votes: Dict[str, Dict[str, str]] = {}  # user -> proposal_id -> vote
        self.logger = logger
        self.proposal_counter = 0
        self.voting_period_days = 3  # Período de votação em dias
        self.approval_threshold = 0.5  # 50% de aprovação necessária
    
    def create_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        proposal_type: str,
        target_parameter: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> str:
        """Cria nova proposta"""
        try:
            # Verificar se proposer tem tokens
            if proposer not in self.token_holders or self.token_holders[proposer] < 100:
                raise ValueError("Proposer não tem saldo mínimo de tokens")
            
            self.proposal_counter += 1
            proposal_id = f"prop_{self.proposal_counter}"
            
            now = datetime.now()
            proposal = Proposal(
                id=proposal_id,
                title=title,
                description=description,
                proposer=proposer,
                proposal_type=proposal_type,
                target_parameter=target_parameter,
                new_value=new_value,
                voting_start=now,
                voting_end=now + timedelta(days=self.voting_period_days),
                status=ProposalStatus.VOTING,
                votes_for=0,
                votes_against=0,
                votes_abstain=0
            )
            
            self.proposals[proposal_id] = proposal
            self.logger.info(f"Proposta criada: {proposal_id} - {title}")
            return proposal_id
        
        except Exception as e:
            self.logger.error(f"Erro ao criar proposta: {e}")
            raise
    
    def vote(
        self,
        voter: str,
        proposal_id: str,
        vote: str  # "for", "against", "abstain"
    ) -> bool:
        """Registra voto em uma proposta"""
        try:
            if proposal_id not in self.proposals:
                raise ValueError(f"Proposta {proposal_id} não encontrada")
            
            proposal = self.proposals[proposal_id]
            
            # Verificar período de votação
            if datetime.now() > proposal.voting_end:
                raise ValueError("Período de votação encerrado")
            
            # Verificar se votante tem tokens
            if voter not in self.token_holders:
                raise ValueError(f"Votante {voter} não encontrado")
            
            voting_power = self.token_holders[voter]
            
            # Verificar se já votou
            if voter in self.user_votes and proposal_id in self.user_votes[voter]:
                raise ValueError("Votante já votou nesta proposta")
            
            # Registrar voto
            if voter not in self.user_votes:
                self.user_votes[voter] = {}
            
            self.user_votes[voter][proposal_id] = vote
            
            # Contabilizar voto
            if vote == "for":
                proposal.votes_for += voting_power
            elif vote == "against":
                proposal.votes_against += voting_power
            else:
                proposal.votes_abstain += voting_power
            
            self.logger.info(f"Voto registrado: {voter} -> {proposal_id} ({vote})")
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao registrar voto: {e}")
            raise
    
    def finalize_proposal(self, proposal_id: str) -> bool:
        """Finaliza votação e executa se aprovada"""
        try:
            if proposal_id not in self.proposals:
                raise ValueError(f"Proposta {proposal_id} não encontrada")
            
            proposal = self.proposals[proposal_id]
            
            # Verificar se votação encerrou
            if datetime.now() < proposal.voting_end:
                raise ValueError("Período de votação ainda não encerrou")
            
            # Calcular resultado
            total_votes = proposal.votes_for + proposal.votes_against
            if total_votes == 0:
                proposal.status = ProposalStatus.REJECTED
                self.logger.warning(f"Proposta {proposal_id} rejeitada: sem votos")
                return False
            
            approval_rate = proposal.votes_for / total_votes
            
            if approval_rate >= self.approval_threshold:
                proposal.status = ProposalStatus.APPROVED
                proposal.execution_timestamp = datetime.now()
                self.logger.info(f"Proposta {proposal_id} APROVADA ({approval_rate*100:.1f}%)")
                return True
            else:
                proposal.status = ProposalStatus.REJECTED
                self.logger.info(f"Proposta {proposal_id} REJEITADA ({approval_rate*100:.1f}%)")
                return False
        
        except Exception as e:
            self.logger.error(f"Erro ao finalizar proposta: {e}")
            raise
    
    def get_proposal_status(self, proposal_id: str) -> Dict:
        """Retorna status detalhado de uma proposta"""
        if proposal_id not in self.proposals:
            return {}
        
        proposal = self.proposals[proposal_id]
        total_votes = proposal.votes_for + proposal.votes_against
        
        return {
            'id': proposal.id,
            'title': proposal.title,
            'status': proposal.status.value,
            'votes_for': proposal.votes_for,
            'votes_against': proposal.votes_against,
            'votes_abstain': proposal.votes_abstain,
            'total_votes': total_votes,
            'approval_rate': (proposal.votes_for / total_votes * 100) if total_votes > 0 else 0,
            'voting_end': proposal.voting_end.isoformat(),
            'type': proposal.proposal_type
        }
    
    def get_all_proposals(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Lista todas as propostas"""
        proposals = []
        for proposal in self.proposals.values():
            if status_filter and proposal.status.value != status_filter:
                continue
            proposals.append(self.get_proposal_status(proposal.id))
        return proposals
    
    def get_treasury_balance(self) -> float:
        """Retorna saldo total de tokens na tesoura"""
        return sum(self.token_holders.values())
    
    def distribute_rewards(self, amount: float, to_address: str):
        """Distribui recompensas de tesoura"""
        try:
            if to_address not in self.token_holders:
                self.token_holders[to_address] = 0
            
            self.token_holders[to_address] += amount
            self.logger.info(f"Recompensa distribuída: {amount} para {to_address}")
        except Exception as e:
            self.logger.error(f"Erro ao distribuir recompensas: {e}")
