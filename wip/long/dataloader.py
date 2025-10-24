"""
Data loading and parsing utilities for CSAT evaluation datasets
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np
import re
from pathlib import Path


class Language(Enum):
    CHINESE = "chinese"
    ENGLISH = "english"


class Speaker(Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"


@dataclass
class Utterance:
    """Single utterance in dialogue"""
    speaker: Speaker
    text: str
    action: Optional[str]
    satisfaction_scores: List[int]
    

@dataclass
class Dialogue:
    """Complete dialogue session"""
    utterances: List[Utterance]
    overall_satisfaction: Optional[List[int]]
    explanations: Optional[List[str]]  # For JDDC dialogue-level explanations
    language: Language
    
    @property
    def average_satisfaction(self) -> float:
        """Calculate average satisfaction score from OVERALL line (1-5 scale)"""
        if self.overall_satisfaction:
            return float(np.mean(self.overall_satisfaction))  # Keep original 1-5 scale
        # Fallback: Calculate from utterance-level scores
        all_scores = []
        for utt in self.utterances:
            if utt.satisfaction_scores:
                all_scores.extend(utt.satisfaction_scores)
        return float(np.mean(all_scores)) if all_scores else 3.0
    
    def to_text(self) -> str:
        """Convert dialogue to text format"""
        lines = []
        for utt in self.utterances:
            lines.append(f"{utt.speaker.value}: {utt.text}")
        return "\n".join(lines)


class ActionMapper:
    """Map JDDC fine-grained actions to categories"""
    
    ACTION_CATEGORIES = {
        '配送': ['配送周期', '物流全程跟踪', '联系配送', '什么时间出库', '配送方式', '返回方式', 
                '预约配送时间', '少商品与少配件', '拒收', '能否自提', '能否配送', '售前运费多少',
                '发错货', '下单地址填写', '发货检查', '京东特色配送', '提前配送', '填写返件运单号',
                '怎么确认收货', '快递单号不正确', '自提时间', '发货时间未到不能出库', 
                '送货上门附加手续费', '夺宝岛配送时间', '夺宝岛运费', '配送超区'],
        '退换': ['保修返修及退换货政策', '正常退款周期', '返修退换货处理周期', '售后运费', 
                '申请退款', '退款到哪儿', '返修退换货拆包装', '取消退款', '在哪里查询退款',
                '退款异常', '团购退款', '补差价'],
        '发票': ['发票退换修改', '查看发票', '是否提供发票', '填写发票信息', '增票相关',
                '电子发票', '补发票', '返修退换货发票'],
        '客服': ['联系客服', '联系客户', '联系商家', '联系售后', '投诉', '夺宝岛售后'],
        '产品咨询': ['属性咨询', '使用咨询', '商品检索', '商品价格咨询', '补货时间', '生产日期',
                   '正品保障', '包装清单', '库存状态', '商品介绍', '外包装', '商品比较',
                   '保修期', '方区别', '补发', '预约抢购', '为什么显示无货', '开箱验货',
                   '全球购解释', '有什么颜色', '套装购买', '是否全国联保', '是什么颜色',
                   '图片差异', '配件推荐', '发表商品咨询', '爱回收解释', '夺宝岛商品来源',
                   '金融理财', 'DIY装机', '众筹说明', '定金解释'],
        '价保': ['价保申请流程', '价保条件', '价保记录查询', '无法申请价保'],
        '支付': ['货到付款', '支付方式', '白条还款方式', '公司转账', '在线支付', '白条分期手续费',
                '白条开通', '无法购买提交', '余额查询', '支付到账时间', '支付密码', '余额使用',
                '库转入转出', '微信支付', '超期未还款', '网银钱包提现异常', '代客户充值',
                '免密支付', '充值失败', '网银钱包定义', '网银钱包开通', '充值到账异常',
                '多次支付退款', '微信下单', '夺宝岛支付方式'],
        'bug': ['下单后无记录', '无法加入购物车', '竞拍异常', '地址信息无法保存'],
        '维修': ['售后维修点查询', '服务单查询'],
        '评价': ['查看评价晒单', '删除修改评价晒单', '评价晒单返券和赠品', '评价晒单异常',
                '评价晒单送积分京豆'],
        '预定': ['机票相关', '购买机票', '火车票', '酒店预订'],
        'OTHER': ['OTHER']
    }
    
    def __init__(self):
        # Create reverse mapping
        self.action_to_category = {}
        for category, actions in self.ACTION_CATEGORIES.items():
            for action in actions:
                self.action_to_category[action] = category
    
    def map_action(self, action: str) -> str:
        """Map fine-grained action to category"""
        if not action:
            return "OTHER"
        return self.action_to_category.get(action, "OTHER")


class DatasetParser:
    """Parse JDDC, MWOZ, and CCPE dataset formats"""
    
    def __init__(self):
        self.action_mapper = ActionMapper()
    
    def parse_file(self, filepath: str, language: Language) -> List[Dialogue]:
        """Parse dataset file into Dialogue objects"""
        dialogues = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines to get sessions
        sessions = content.strip().split('\n\n')
        
        for session in sessions:
            if not session.strip():
                continue
                
            dialogue = self._parse_session(session, language)
            if dialogue:
                dialogues.append(dialogue)
        
        return dialogues
    
    def _parse_session(self, session_text: str, language: Language) -> Optional[Dialogue]:
        """Parse a single session"""
        lines = session_text.strip().split('\n')
        utterances = []
        overall_satisfaction = None
        explanations = None
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split('\t')
            
            # Check if this is an OVERALL line
            if len(parts) >= 2 and parts[1].strip() == 'OVERALL':
                # Parse overall satisfaction scores
                if len(parts) >= 4 and parts[3].strip():
                    scores_str = parts[3].strip()
                    overall_satisfaction = self._parse_scores(scores_str)
                
                # Parse explanations (for JDDC)
                if len(parts) >= 5 and parts[4]:
                    explanations = parts[4].split(';')
                continue
            
            # Parse regular utterance
            if len(parts) >= 2:
                speaker_str = parts[0].strip()
                text = parts[1].strip()
                action = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
                
                # Map action to category for JDDC
                if language == Language.CHINESE and action:
                    action = self.action_mapper.map_action(action)
                
                # Parse satisfaction scores
                satisfaction_scores = []
                if len(parts) > 3 and parts[3].strip():
                    satisfaction_scores = self._parse_scores(parts[3].strip())
                
                try:
                    speaker = Speaker(speaker_str)
                    utterances.append(Utterance(
                        speaker=speaker,
                        text=text,
                        action=action,
                        satisfaction_scores=satisfaction_scores
                    ))
                except ValueError:
                    continue  # Skip invalid speaker roles
        
        if utterances:
            return Dialogue(
                utterances=utterances,
                overall_satisfaction=overall_satisfaction,
                explanations=explanations,
                language=language
            )
        return None
    
    @staticmethod
    def _parse_scores(scores_str: str) -> List[int]:
        """Parse satisfaction scores from string"""
        scores = []
        for score in scores_str.split(','):
            try:
                scores.append(int(score.strip()))
            except ValueError:
                continue
        return scores


def load_dataset(dataset_name: str) -> List[Dialogue]:
    """Load dataset by name"""
    dataset_path = Path(__file__).parent / 'dataset' / f'{dataset_name}.txt'
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset {dataset_name} not found at {dataset_path}")
    
    # Determine language based on dataset name
    if dataset_name == 'JDDC':
        language = Language.CHINESE
    else:
        language = Language.ENGLISH  # MWOZ, CCPE, etc.
    
    parser = DatasetParser()
    return parser.parse_file(str(dataset_path), language)
