"""
Blawx file parser service.

This module parses .blawx fil        # Parse YAML documents
        documents = list(yaml.safe_load_all(content))
        
        # Debug: check what we loaded
        print(f"Loaded {len(documents)} documents")
        if documents:
            print(f"First document type: {type(documents[0])}")
            if isinstance(documents[0], dict):
                print(f"First document keys: {list(documents[0].keys())}")
        
        ruledoc = None
        workspaces = []
        
        for doc in documents:
            if isinstance(doc, dict) and doc.get('model') == 'blawx.ruledoc':
                ruledoc = doc
            elif isinstance(doc, dict) and doc.get('model') == 'blawx.workspace':
                workspaces.append(doc)ormat) and extracts:
- Legal rule text
- s(CASP) logic programs
- Structured legal relationships
- Navigation trees for legal provisions
"""

import yaml
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass
class LegalProvision:
    """Represents a legal provision with its text and metadata."""
    id: str
    title: str
    text: str
    section_number: Optional[str] = None
    subsection_number: Optional[str] = None
    parent_id: Optional[str] = None


@dataclass
class ScaspRule:
    """Represents an s(CASP) rule with metadata."""
    rule_text: str
    rule_type: str  # 'fact', 'rule', 'query', 'abducible'
    variables: List[str]
    predicates: List[str]


@dataclass
class LegalRuleDoc:
    """Complete parsed legal rule document."""
    name: str
    slug: str
    provisions: List[LegalProvision]
    scasp_rules: List[ScaspRule]
    relationships: Dict[str, List[str]]
    categories: List[str]
    xml_content: Optional[str] = None


class BlawxParser:
    """Parser for .blawx files."""
    
    def __init__(self):
        self.akoma_ntoso_ns = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
    
    def parse_file(self, file_path: str) -> LegalRuleDoc:
        """Parse a .blawx file and return structured legal data."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse YAML documents - the file contains a list of documents
        docs_list = list(yaml.safe_load_all(content))
        
        # The YAML file actually contains a single list of documents
        if len(docs_list) == 1 and isinstance(docs_list[0], list):
            documents = docs_list[0]
        else:
            documents = docs_list
        
        ruledoc = None
        workspaces = []
        
        for doc in documents:
            if isinstance(doc, dict) and doc.get('model') == 'blawx.ruledoc':
                ruledoc = doc
            elif isinstance(doc, dict) and doc.get('model') == 'blawx.workspace':
                workspaces.append(doc)
        
        if not ruledoc:
            raise ValueError("No ruledoc found in .blawx file")
        
        return self._parse_ruledoc(ruledoc, workspaces)
    
    def _parse_ruledoc(self, ruledoc: dict, workspaces: List[dict]) -> LegalRuleDoc:
        """Parse the main rule document."""
        fields = ruledoc['fields']
        
        # Parse legal provisions from AkomaNtoso XML
        provisions = self._parse_akoma_ntoso(fields.get('akoma_ntoso', ''))
        
        # Parse s(CASP) rules from workspaces
        scasp_rules = []
        categories = []
        relationships = {}
        
        for workspace in workspaces:
            ws_fields = workspace['fields']
            
            # Parse s(CASP) encoding
            if ws_fields.get('scasp_encoding'):
                rules = self._parse_scasp_encoding(ws_fields['scasp_encoding'])
                scasp_rules.extend(rules)
            
            # Parse XML content for categories and relationships
            if ws_fields.get('xml_content'):
                cats, rels = self._parse_blockly_xml(ws_fields['xml_content'])
                categories.extend(cats)
                relationships.update(rels)
        
        return LegalRuleDoc(
            name=fields['ruledoc_name'],
            slug=fields['rule_slug'],
            provisions=provisions,
            scasp_rules=scasp_rules,
            relationships=relationships,
            categories=list(set(categories)),
            xml_content=fields.get('akoma_ntoso')
        )
    
    def _parse_akoma_ntoso(self, xml_content: str) -> List[LegalProvision]:
        """Parse AkomaNtoso XML to extract legal provisions."""
        if not xml_content:
            return []
        
        provisions = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Find all sections, subsections, and paragraphs
            for elem in root.iter():
                if elem.tag.endswith('section'):
                    provision = self._parse_xml_element(elem, 'section')
                    if provision:
                        provisions.append(provision)
                elif elem.tag.endswith('subSection'):
                    provision = self._parse_xml_element(elem, 'subsection')
                    if provision:
                        provisions.append(provision)
                elif elem.tag.endswith('paragraph'):
                    provision = self._parse_xml_element(elem, 'paragraph')
                    if provision:
                        provisions.append(provision)
        
        except ET.ParseError as e:
            print(f"Warning: Could not parse AkomaNtoso XML: {e}")
        
        return provisions
    
    def _parse_xml_element(self, elem, element_type: str) -> Optional[LegalProvision]:
        """Parse an individual XML element into a LegalProvision."""
        eid = elem.get('eId')
        if not eid:
            return None
        
        # Extract number
        num_elem = elem.find('.//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}num')
        number = num_elem.text if num_elem is not None else None
        
        # Extract text content
        text_parts = []
        for text_elem in elem.iter():
            if text_elem.tag.endswith('p') and text_elem.text:
                text_parts.append(text_elem.text.strip())
        
        text = ' '.join(text_parts)
        
        return LegalProvision(
            id=eid,
            title=f"{element_type.title()} {number}" if number else element_type.title(),
            text=text,
            section_number=number if element_type == 'section' else None,
            subsection_number=number if element_type == 'subsection' else None
        )
    
    def _parse_scasp_encoding(self, scasp_text: str) -> List[ScaspRule]:
        """Parse s(CASP) logic program text."""
        rules = []
        
        lines = scasp_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):  # Skip empty lines and comments
                continue
            
            rule = self._parse_scasp_line(line)
            if rule:
                rules.append(rule)
        
        return rules
    
    def _parse_scasp_line(self, line: str) -> Optional[ScaspRule]:
        """Parse a single s(CASP) line."""
        line = line.strip()
        
        # Skip empty lines, comments, or malformed lines
        if not line or line.startswith('%') or line == '.' or line.endswith(',.'):
            return None
            
        # Clean up common syntax issues
        line = line.rstrip('.,')  # Remove trailing periods and commas
        if not line:
            return None
        
        # Determine rule type
        if line.startswith('#abducible'):
            rule_type = 'abducible'
            rule_text = line[10:].strip()  # Remove '#abducible '
        elif line.startswith('?-'):
            rule_type = 'query'
            rule_text = line[2:].strip()  # Remove '?- '
        elif line.startswith('#pred'):
            rule_type = 'fact'  # Predicate definitions are treated as facts
            rule_text = line
        elif line.startswith(':-'):
            rule_type = 'rule'
            rule_text = line
        elif ':-' in line:
            rule_type = 'rule'
            rule_text = line
        else:
            rule_type = 'fact'
            rule_text = line
        
        # Skip if rule text is empty after cleaning
        if not rule_text:
            return None
        
        # Extract variables (uppercase words)
        variables = re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', rule_text)
        
        # Extract predicates (lowercase words followed by parentheses)
        predicates = re.findall(r'\b[a-z][a-zA-Z0-9_]*(?=\s*\()', rule_text)
        
        return ScaspRule(
            rule_text=rule_text,
            rule_type=rule_type,
            variables=list(set(variables)),
            predicates=list(set(predicates))
        )
    
    def _parse_blockly_xml(self, xml_content: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """Parse Blockly XML content to extract categories and relationships."""
        categories = []
        relationships = {}
        
        try:
            root = ET.fromstring(xml_content)
            
            # Find category declarations
            for block in root.findall('.//block[@type="new_category_declaration"]'):
                field = block.find('.//field[@name="category_name"]')
                if field is not None and field.text:
                    categories.append(field.text)
            
            # Find relationship declarations
            for block in root.findall('.//block'):
                block_type = block.get('type', '')
                if 'relationship' in block_type or 'attribute' in block_type:
                    # Extract relationship information
                    mutation = block.find('mutation')
                    if mutation is not None:
                        rel_name = mutation.get('relationship_name') or mutation.get('attributename')
                        if rel_name:
                            relationships[rel_name] = []
        
        except ET.ParseError as e:
            print(f"Warning: Could not parse Blockly XML: {e}")
        
        return categories, relationships
    
    def extract_facts_for_query(self, doc: LegalRuleDoc, query_terms: List[str]) -> List[ScaspRule]:
        """Extract relevant facts and rules for a specific query."""
        relevant_rules = []
        
        # Find rules that contain any of the query terms
        for rule in doc.scasp_rules:
            if any(term.lower() in rule.rule_text.lower() for term in query_terms):
                relevant_rules.append(rule)
            elif any(predicate in query_terms for predicate in rule.predicates):
                relevant_rules.append(rule)
        
        return relevant_rules
    
    def format_scasp_program(self, rules: List[ScaspRule]) -> str:
        """Format s(CASP) rules into a complete logic program."""
        program_lines = []
        
        # Group rules by type
        facts = [r for r in rules if r.rule_type == 'fact']
        logic_rules = [r for r in rules if r.rule_type == 'rule']
        abducibles = [r for r in rules if r.rule_type == 'abducible']
        queries = [r for r in rules if r.rule_type == 'query']
        
        # Add facts
        if facts:
            program_lines.append("% Facts")
            for rule in facts:
                # Ensure rule ends with period if it doesn't already
                rule_text = rule.rule_text.rstrip('.')
                if rule_text and not rule_text.endswith('.'):
                    rule_text += '.'
                if rule_text:  # Only add non-empty rules
                    program_lines.append(rule_text)
            program_lines.append("")
        
        # Add abducibles
        if abducibles:
            program_lines.append("% Abducibles")
            for rule in abducibles:
                rule_text = rule.rule_text.rstrip('.')
                if rule_text:
                    program_lines.append(f"#abducible {rule_text}.")
            program_lines.append("")
        
        # Add rules
        if logic_rules:
            program_lines.append("% Rules")
            for rule in logic_rules:
                rule_text = rule.rule_text.rstrip('.')
                if rule_text and not rule_text.endswith('.'):
                    rule_text += '.'
                if rule_text:  # Only add non-empty rules
                    program_lines.append(rule_text)
            program_lines.append("")
        
        # Add queries
        if queries:
            program_lines.append("% Queries")
            for rule in queries:
                rule_text = rule.rule_text.rstrip('.')
                if rule_text:
                    program_lines.append(f"?- {rule_text}.")
        
        return '\n'.join(program_lines)


def main():
    """Test the parser with the sample file."""
    parser = BlawxParser()
    
    try:
        doc = parser.parse_file('/Users/wmoussa/src/racx/legal-ai-assistant/data/mperron_access-to-information-act-s4.blawx')
        
        print(f"Parsed document: {doc.name}")
        print(f"Provisions: {len(doc.provisions)}")
        print(f"s(CASP) rules: {len(doc.scasp_rules)}")
        print(f"Categories: {doc.categories}")
        
        # Show sample provision
        if doc.provisions:
            print(f"\nSample provision: {doc.provisions[0].title}")
            print(f"Text: {doc.provisions[0].text[:200]}...")
        
        # Show sample rule
        if doc.scasp_rules:
            print(f"\nSample s(CASP) rule: {doc.scasp_rules[0].rule_text}")
            
        # Format complete program
        program = parser.format_scasp_program(doc.scasp_rules)
        print(f"\nGenerated s(CASP) program ({len(program)} chars)")
        
    except Exception as e:
        print(f"Error parsing file: {e}")


if __name__ == "__main__":
    main()