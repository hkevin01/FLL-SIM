"""
Visual Block Programming Interface for FLL-Sim

Provides drag-and-drop programming blocks that generate Python code for
robot control. Includes block editor, code generation, and real-time preview.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fll_sim.education.interactive_tutorial_system import (
    BlockType, InteractiveTutorialSystem, ProgrammingBlock)
from fll_sim.utils.logger import FLLLogger


class BlockConnectionType(Enum):
    """Types of block connections."""
    PREVIOUS = "previous"
    NEXT = "next"
    INPUT = "input"
    OUTPUT = "output"


@dataclass
class BlockConnection:
    """Represents a connection point on a block."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: BlockConnectionType = BlockConnectionType.NEXT
    data_type: str = "any"
    required: bool = False
    connected_to: Optional[str] = None


@dataclass
class VisualBlock:
    """Visual representation of a programming block in the editor."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    block_definition_id: str = ""
    position: Tuple[float, float] = (0, 0)
    input_values: Dict[str, Any] = field(default_factory=dict)
    connections: Dict[str, BlockConnection] = field(default_factory=dict)
    is_selected: bool = False
    is_error: bool = False
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BlockConnection:
    """Connection between blocks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_block_id: str = ""
    to_block_id: str = ""
    from_connection: str = ""
    to_connection: str = ""


@dataclass
class VisualProgram:
    """Complete visual programming workspace."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Program"
    description: str = ""
    blocks: Dict[str, VisualBlock] = field(default_factory=dict)
    connections: Dict[str, BlockConnection] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    canvas_size: Tuple[int, int] = (1200, 800)
    zoom_level: float = 1.0
    scroll_position: Tuple[float, float] = (0, 0)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_running: bool = False


class VisualProgrammingInterface:
    """Main visual programming interface for block-based coding."""

    def __init__(self, tutorial_system: InteractiveTutorialSystem):
        self.logger = FLLLogger('VisualProgrammingInterface')
        self.tutorial_system = tutorial_system

        # Current workspace
        self.current_program: Optional[VisualProgram] = None
        self.saved_programs: Dict[str, VisualProgram] = {}

        # Editor state
        self.selected_blocks: List[str] = []
        self.clipboard: List[VisualBlock] = []
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []

        # Block palette
        self.block_palette = self._create_block_palette()

        # Event handlers
        self.event_handlers: Dict[str, List] = {
            'block_added': [],
            'block_removed': [],
            'block_connected': [],
            'block_disconnected': [],
            'program_changed': [],
            'code_generated': []
        }

        self.logger.info("Visual Programming Interface initialized")

    def _create_block_palette(self) -> Dict[str, List[ProgrammingBlock]]:
        """Create organized block palette."""
        palette = {}

        for block in self.tutorial_system.programming_blocks.values():
            category = block.category
            if category not in palette:
                palette[category] = []
            palette[category].append(block)

        # Sort categories and blocks
        for category in palette:
            palette[category].sort(key=lambda b: b.name)

        return palette

    # Program Management
    def create_new_program(self, name: str = "New Program") -> str:
        """Create a new visual program."""
        program = VisualProgram(name=name)
        self.current_program = program
        self.saved_programs[program.id] = program

        self._save_state_for_undo()
        self._emit_event('program_changed', program)

        self.logger.info(f"Created new program: {name}")
        return program.id

    def load_program(self, program_id: str) -> bool:
        """Load an existing program."""
        if program_id not in self.saved_programs:
            self.logger.error(f"Program not found: {program_id}")
            return False

        self.current_program = self.saved_programs[program_id]
        self._clear_undo_redo()
        self._emit_event('program_changed', self.current_program)

        self.logger.info(f"Loaded program: {self.current_program.name}")
        return True

    def save_program(self, program_id: Optional[str] = None) -> bool:
        """Save the current program."""
        if not self.current_program:
            return False

        program_id = program_id or self.current_program.id
        self.current_program.updated_at = datetime.now()
        self.saved_programs[program_id] = self.current_program

        self.logger.info(f"Saved program: {self.current_program.name}")
        return True

    def duplicate_program(self, program_id: str, new_name: str) -> Optional[str]:
        """Duplicate an existing program."""
        if program_id not in self.saved_programs:
            return None

        original = self.saved_programs[program_id]
        duplicate = VisualProgram(
            name=new_name,
            description=original.description,
            blocks={bid: VisualBlock(
                block_definition_id=block.block_definition_id,
                position=block.position,
                input_values=block.input_values.copy()
            ) for bid, block in original.blocks.items()},
            variables=original.variables.copy(),
            canvas_size=original.canvas_size,
            zoom_level=original.zoom_level
        )

        self.saved_programs[duplicate.id] = duplicate
        self.logger.info(f"Duplicated program: {new_name}")
        return duplicate.id

    # Block Management
    def add_block(self, block_definition_id: str, position: Tuple[float, float],
                  input_values: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add a block to the current program."""
        if not self.current_program:
            return None

        block_definition = self.tutorial_system.get_programming_block(
            block_definition_id
        )
        if not block_definition:
            self.logger.error(f"Block definition not found: {block_definition_id}")
            return None

        visual_block = VisualBlock(
            block_definition_id=block_definition_id,
            position=position,
            input_values=input_values or {}
        )

        # Initialize connections based on block type
        self._initialize_block_connections(visual_block, block_definition)

        self.current_program.blocks[visual_block.id] = visual_block
        self.current_program.updated_at = datetime.now()

        self._save_state_for_undo()
        self._emit_event('block_added', visual_block)

        self.logger.debug(f"Added block: {block_definition.name}")
        return visual_block.id

    def _initialize_block_connections(self, visual_block: VisualBlock,
                                    block_definition: ProgrammingBlock):
        """Initialize connection points for a block."""
        connections = {}

        # Most blocks have previous/next connections for sequence
        if block_definition.type != BlockType.EVENT:
            connections['previous'] = BlockConnection(
                type=BlockConnectionType.PREVIOUS
            )
            connections['next'] = BlockConnection(
                type=BlockConnectionType.NEXT
            )

        # Add input connections
        for i, input_def in enumerate(block_definition.inputs):
            connections[f'input_{i}'] = BlockConnection(
                type=BlockConnectionType.INPUT,
                data_type=input_def.get('type', 'any'),
                required=input_def.get('required', False)
            )

        # Add output connections
        for i, output_def in enumerate(block_definition.outputs):
            connections[f'output_{i}'] = BlockConnection(
                type=BlockConnectionType.OUTPUT,
                data_type=output_def.get('type', 'any')
            )

        visual_block.connections = connections

    def remove_block(self, block_id: str) -> bool:
        """Remove a block from the current program."""
        if not self.current_program or block_id not in self.current_program.blocks:
            return False

        # Remove all connections to/from this block
        self._remove_block_connections(block_id)

        # Remove the block
        del self.current_program.blocks[block_id]
        self.current_program.updated_at = datetime.now()

        self._save_state_for_undo()
        self._emit_event('block_removed', block_id)

        self.logger.debug(f"Removed block: {block_id}")
        return True

    def _remove_block_connections(self, block_id: str):
        """Remove all connections to/from a block."""
        if not self.current_program:
            return

        connections_to_remove = []
        for conn_id, connection in self.current_program.connections.items():
            if (connection.from_block_id == block_id or
                connection.to_block_id == block_id):
                connections_to_remove.append(conn_id)

        for conn_id in connections_to_remove:
            del self.current_program.connections[conn_id]

    def move_block(self, block_id: str, new_position: Tuple[float, float]) -> bool:
        """Move a block to a new position."""
        if (not self.current_program or
            block_id not in self.current_program.blocks):
            return False

        self.current_program.blocks[block_id].position = new_position
        self.current_program.updated_at = datetime.now()

        return True

    def update_block_inputs(self, block_id: str,
                          input_values: Dict[str, Any]) -> bool:
        """Update input values for a block."""
        if (not self.current_program or
            block_id not in self.current_program.blocks):
            return False

        block = self.current_program.blocks[block_id]
        block.input_values.update(input_values)
        self.current_program.updated_at = datetime.now()

        # Validate inputs
        self._validate_block(block_id)

        return True

    # Block Connections
    def connect_blocks(self, from_block_id: str, from_connection: str,
                      to_block_id: str, to_connection: str) -> Optional[str]:
        """Connect two blocks."""
        if not self.current_program:
            return None

        # Validate connection
        if not self._can_connect_blocks(from_block_id, from_connection,
                                      to_block_id, to_connection):
            return None

        # Remove existing connections at target
        self._remove_connection_at(to_block_id, to_connection)

        # Create new connection
        connection = BlockConnection(
            from_block_id=from_block_id,
            to_block_id=to_block_id,
            from_connection=from_connection,
            to_connection=to_connection
        )

        self.current_program.connections[connection.id] = connection

        # Update block connection references
        from_block = self.current_program.blocks[from_block_id]
        to_block = self.current_program.blocks[to_block_id]

        from_block.connections[from_connection].connected_to = connection.id
        to_block.connections[to_connection].connected_to = connection.id

        self._save_state_for_undo()
        self._emit_event('block_connected', connection)

        self.logger.debug(f"Connected blocks: {from_block_id} -> {to_block_id}")
        return connection.id

    def _can_connect_blocks(self, from_block_id: str, from_connection: str,
                          to_block_id: str, to_connection: str) -> bool:
        """Check if two blocks can be connected."""
        if from_block_id == to_block_id:
            return False

        if (from_block_id not in self.current_program.blocks or
            to_block_id not in self.current_program.blocks):
            return False

        from_block = self.current_program.blocks[from_block_id]
        to_block = self.current_program.blocks[to_block_id]

        if (from_connection not in from_block.connections or
            to_connection not in to_block.connections):
            return False

        from_conn = from_block.connections[from_connection]
        to_conn = to_block.connections[to_connection]

        # Check connection type compatibility
        if from_conn.type == BlockConnectionType.OUTPUT:
            if to_conn.type != BlockConnectionType.INPUT:
                return False
        elif from_conn.type == BlockConnectionType.NEXT:
            if to_conn.type != BlockConnectionType.PREVIOUS:
                return False
        else:
            return False

        # Check data type compatibility
        if (from_conn.data_type != "any" and to_conn.data_type != "any" and
            from_conn.data_type != to_conn.data_type):
            return False

        # Check for circular dependencies
        if self._would_create_cycle(from_block_id, to_block_id):
            return False

        return True

    def _would_create_cycle(self, from_block_id: str, to_block_id: str) -> bool:
        """Check if connecting blocks would create a circular dependency."""
        # Simple cycle detection - check if to_block eventually connects to from_block
        visited = set()
        stack = [to_block_id]

        while stack:
            current_id = stack.pop()
            if current_id in visited:
                continue
            if current_id == from_block_id:
                return True

            visited.add(current_id)

            # Find all blocks this one connects to
            for connection in self.current_program.connections.values():
                if connection.from_block_id == current_id:
                    stack.append(connection.to_block_id)

        return False

    def _remove_connection_at(self, block_id: str, connection_point: str):
        """Remove any existing connection at a specific point."""
        if not self.current_program:
            return

        block = self.current_program.blocks.get(block_id)
        if not block or connection_point not in block.connections:
            return

        connection_ref = block.connections[connection_point].connected_to
        if connection_ref and connection_ref in self.current_program.connections:
            del self.current_program.connections[connection_ref]
            block.connections[connection_point].connected_to = None

    def disconnect_blocks(self, connection_id: str) -> bool:
        """Disconnect two blocks."""
        if (not self.current_program or
            connection_id not in self.current_program.connections):
            return False

        connection = self.current_program.connections[connection_id]

        # Clear connection references in blocks
        from_block = self.current_program.blocks[connection.from_block_id]
        to_block = self.current_program.blocks[connection.to_block_id]

        from_block.connections[connection.from_connection].connected_to = None
        to_block.connections[connection.to_connection].connected_to = None

        # Remove connection
        del self.current_program.connections[connection_id]

        self._save_state_for_undo()
        self._emit_event('block_disconnected', connection)

        self.logger.debug(f"Disconnected blocks: {connection.from_block_id} -> {connection.to_block_id}")
        return True

    # Code Generation
    def generate_code(self) -> str:
        """Generate Python code from the visual program."""
        if not self.current_program:
            return ""

        # Find entry points (blocks with no previous connection)
        entry_blocks = []
        for block in self.current_program.blocks.values():
            if 'previous' in block.connections:
                if not block.connections['previous'].connected_to:
                    entry_blocks.append(block)

        if not entry_blocks:
            return "# No entry points found"

        code_lines = []
        code_lines.append("# Generated code from visual programming interface")
        code_lines.append("import time")
        code_lines.append("")

        # Generate code for each sequence
        for entry_block in entry_blocks:
            sequence_code = self._generate_sequence_code(entry_block.id)
            code_lines.extend(sequence_code)
            code_lines.append("")

        generated_code = "\n".join(code_lines)
        self._emit_event('code_generated', generated_code)

        return generated_code

    def _generate_sequence_code(self, start_block_id: str,
                              visited: Optional[set] = None) -> List[str]:
        """Generate code for a sequence of connected blocks."""
        if visited is None:
            visited = set()

        if start_block_id in visited:
            return ["# Circular reference detected"]

        visited.add(start_block_id)
        code_lines = []
        current_block_id = start_block_id

        while current_block_id:
            block = self.current_program.blocks[current_block_id]
            block_definition = self.tutorial_system.get_programming_block(
                block.block_definition_id
            )

            if not block_definition:
                code_lines.append(f"# Unknown block: {current_block_id}")
                break

            # Generate code for this block
            block_code = self._generate_block_code(block, block_definition)
            if block_code:
                code_lines.append(block_code)

            # Find next block
            next_block_id = None
            if 'next' in block.connections:
                connection_id = block.connections['next'].connected_to
                if connection_id and connection_id in self.current_program.connections:
                    connection = self.current_program.connections[connection_id]
                    next_block_id = connection.to_block_id

            current_block_id = next_block_id

        return code_lines

    def _generate_block_code(self, block: VisualBlock,
                           block_definition: ProgrammingBlock) -> str:
        """Generate code for a single block."""
        # Start with the code template
        code = block_definition.code_template

        # Replace input placeholders
        for i, input_def in enumerate(block_definition.inputs):
            input_name = input_def['name']
            placeholder = f"{{{input_name}}}"

            # Get value from block inputs or use default
            if input_name in block.input_values:
                value = block.input_values[input_name]
            else:
                value = input_def.get('default', '')

            # Handle different value types
            if isinstance(value, str) and input_def.get('type') == 'string':
                value = f"'{value}'"

            code = code.replace(placeholder, str(value))

        return code

    # Validation
    def validate_program(self) -> Dict[str, Any]:
        """Validate the current visual program."""
        if not self.current_program:
            return {'is_valid': False, 'errors': ['No program loaded']}

        errors = []
        warnings = []

        # Check for disconnected blocks
        disconnected_blocks = []
        for block_id, block in self.current_program.blocks.items():
            if self._is_block_disconnected(block):
                disconnected_blocks.append(block_id)

        if disconnected_blocks:
            warnings.append(
                f"Disconnected blocks found: {len(disconnected_blocks)}"
            )

        # Check for missing required inputs
        for block_id, block in self.current_program.blocks.items():
            missing_inputs = self._get_missing_required_inputs(block)
            if missing_inputs:
                errors.append(
                    f"Block {block_id} missing required inputs: {missing_inputs}"
                )

        # Check for circular dependencies
        cycles = self._find_cycles()
        if cycles:
            errors.append(f"Circular dependencies detected: {len(cycles)}")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'disconnected_blocks': disconnected_blocks
        }

    def _is_block_disconnected(self, block: VisualBlock) -> bool:
        """Check if a block is disconnected from the main program flow."""
        # A block is disconnected if it has no previous connection and
        # no connections to other blocks
        if 'previous' not in block.connections:
            return False  # Entry blocks are not considered disconnected

        has_connections = any(
            conn.connected_to for conn in block.connections.values()
        )

        return not has_connections

    def _get_missing_required_inputs(self, block: VisualBlock) -> List[str]:
        """Get list of missing required inputs for a block."""
        block_definition = self.tutorial_system.get_programming_block(
            block.block_definition_id
        )
        if not block_definition:
            return []

        missing = []
        for input_def in block_definition.inputs:
            input_name = input_def['name']
            if (input_def.get('required', False) and
                input_name not in block.input_values):
                missing.append(input_name)

        return missing

    def _find_cycles(self) -> List[List[str]]:
        """Find circular dependencies in the program."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(block_id: str, path: List[str]) -> bool:
            if block_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(block_id)
                cycles.append(path[cycle_start:] + [block_id])
                return True

            if block_id in visited:
                return False

            visited.add(block_id)
            rec_stack.add(block_id)
            path.append(block_id)

            # Check all outgoing connections
            for connection in self.current_program.connections.values():
                if connection.from_block_id == block_id:
                    if dfs(connection.to_block_id, path.copy()):
                        break

            rec_stack.remove(block_id)
            return False

        for block_id in self.current_program.blocks:
            if block_id not in visited:
                dfs(block_id, [])

        return cycles

    def _validate_block(self, block_id: str):
        """Validate a specific block and update its error state."""
        if not self.current_program or block_id not in self.current_program.blocks:
            return

        block = self.current_program.blocks[block_id]
        missing_inputs = self._get_missing_required_inputs(block)

        if missing_inputs:
            block.is_error = True
            block.error_message = f"Missing required inputs: {', '.join(missing_inputs)}"
        else:
            block.is_error = False
            block.error_message = ""

    # Undo/Redo System
    def _save_state_for_undo(self):
        """Save current state for undo functionality."""
        if not self.current_program:
            return

        state = {
            'blocks': {bid: self._serialize_block(block)
                      for bid, block in self.current_program.blocks.items()},
            'connections': {cid: self._serialize_connection(conn)
                          for cid, conn in self.current_program.connections.items()},
            'variables': self.current_program.variables.copy()
        }

        self.undo_stack.append(state)
        self.redo_stack.clear()

        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _serialize_block(self, block: VisualBlock) -> Dict[str, Any]:
        """Serialize a block for undo/redo."""
        return {
            'id': block.id,
            'block_definition_id': block.block_definition_id,
            'position': block.position,
            'input_values': block.input_values.copy()
        }

    def _serialize_connection(self, connection: BlockConnection) -> Dict[str, Any]:
        """Serialize a connection for undo/redo."""
        return {
            'id': connection.id,
            'from_block_id': connection.from_block_id,
            'to_block_id': connection.to_block_id,
            'from_connection': connection.from_connection,
            'to_connection': connection.to_connection
        }

    def _clear_undo_redo(self):
        """Clear undo/redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def undo(self) -> bool:
        """Undo the last action."""
        if not self.undo_stack or not self.current_program:
            return False

        # Save current state to redo stack
        current_state = {
            'blocks': {bid: self._serialize_block(block)
                      for bid, block in self.current_program.blocks.items()},
            'connections': {cid: self._serialize_connection(conn)
                          for cid, conn in self.current_program.connections.items()},
            'variables': self.current_program.variables.copy()
        }
        self.redo_stack.append(current_state)

        # Restore previous state
        previous_state = self.undo_stack.pop()
        self._restore_state(previous_state)

        self.logger.debug("Undo performed")
        return True

    def redo(self) -> bool:
        """Redo the last undone action."""
        if not self.redo_stack or not self.current_program:
            return False

        # Save current state to undo stack
        current_state = {
            'blocks': {bid: self._serialize_block(block)
                      for bid, block in self.current_program.blocks.items()},
            'connections': {cid: self._serialize_connection(conn)
                          for cid, conn in self.current_program.connections.items()},
            'variables': self.current_program.variables.copy()
        }
        self.undo_stack.append(current_state)

        # Restore next state
        next_state = self.redo_stack.pop()
        self._restore_state(next_state)

        self.logger.debug("Redo performed")
        return True

    def _restore_state(self, state: Dict[str, Any]):
        """Restore program state from serialized data."""
        if not self.current_program:
            return

        # Clear current state
        self.current_program.blocks.clear()
        self.current_program.connections.clear()

        # Restore blocks
        for block_data in state['blocks'].values():
            block = VisualBlock(
                id=block_data['id'],
                block_definition_id=block_data['block_definition_id'],
                position=block_data['position'],
                input_values=block_data['input_values']
            )

            # Reinitialize connections
            block_definition = self.tutorial_system.get_programming_block(
                block.block_definition_id
            )
            if block_definition:
                self._initialize_block_connections(block, block_definition)

            self.current_program.blocks[block.id] = block

        # Restore connections
        for conn_data in state['connections'].values():
            connection = BlockConnection(
                id=conn_data['id'],
                from_block_id=conn_data['from_block_id'],
                to_block_id=conn_data['to_block_id'],
                from_connection=conn_data['from_connection'],
                to_connection=conn_data['to_connection']
            )
            self.current_program.connections[connection.id] = connection

        # Restore variables
        self.current_program.variables = state['variables']

        self.current_program.updated_at = datetime.now()

    # Event System
    def add_event_handler(self, event_type: str, handler):
        """Add an event handler."""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler):
        """Remove an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)

    def _emit_event(self, event_type: str, data: Any):
        """Emit an event to all registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")

    # Import/Export
    def export_program(self, program_id: Optional[str] = None) -> Dict[str, Any]:
        """Export a program to a dictionary."""
        program = (self.saved_programs.get(program_id) if program_id
                  else self.current_program)

        if not program:
            return {}

        return {
            'id': program.id,
            'name': program.name,
            'description': program.description,
            'blocks': [self._serialize_block(block)
                      for block in program.blocks.values()],
            'connections': [self._serialize_connection(conn)
                          for conn in program.connections.values()],
            'variables': program.variables,
            'canvas_size': program.canvas_size,
            'zoom_level': program.zoom_level,
            'created_at': program.created_at.isoformat(),
            'updated_at': program.updated_at.isoformat(),
            'version': '1.0'
        }

    def import_program(self, program_data: Dict[str, Any]) -> Optional[str]:
        """Import a program from a dictionary."""
        try:
            program = VisualProgram(
                id=program_data.get('id', str(uuid.uuid4())),
                name=program_data['name'],
                description=program_data.get('description', ''),
                variables=program_data.get('variables', {}),
                canvas_size=tuple(program_data.get('canvas_size', [1200, 800])),
                zoom_level=program_data.get('zoom_level', 1.0),
                created_at=datetime.fromisoformat(program_data['created_at']),
                updated_at=datetime.fromisoformat(program_data['updated_at'])
            )

            # Import blocks
            for block_data in program_data['blocks']:
                block = VisualBlock(
                    id=block_data['id'],
                    block_definition_id=block_data['block_definition_id'],
                    position=tuple(block_data['position']),
                    input_values=block_data['input_values']
                )

                # Reinitialize connections
                block_definition = self.tutorial_system.get_programming_block(
                    block.block_definition_id
                )
                if block_definition:
                    self._initialize_block_connections(block, block_definition)

                program.blocks[block.id] = block

            # Import connections
            for conn_data in program_data['connections']:
                connection = BlockConnection(
                    id=conn_data['id'],
                    from_block_id=conn_data['from_block_id'],
                    to_block_id=conn_data['to_block_id'],
                    from_connection=conn_data['from_connection'],
                    to_connection=conn_data['to_connection']
                )
                program.connections[connection.id] = connection

            self.saved_programs[program.id] = program
            self.logger.info(f"Imported program: {program.name}")

            return program.id

        except Exception as e:
            self.logger.error(f"Failed to import program: {e}")
            return None

    # Utility Methods
    def get_block_palette(self) -> Dict[str, List[ProgrammingBlock]]:
        """Get the organized block palette."""
        return self.block_palette

    def get_current_program_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current program."""
        if not self.current_program:
            return None

        return {
            'id': self.current_program.id,
            'name': self.current_program.name,
            'description': self.current_program.description,
            'block_count': len(self.current_program.blocks),
            'connection_count': len(self.current_program.connections),
            'is_valid': self.validate_program()['is_valid'],
            'created_at': self.current_program.created_at,
            'updated_at': self.current_program.updated_at
        }

    def get_program_list(self) -> List[Dict[str, Any]]:
        """Get list of all saved programs."""
        return [
            {
                'id': program.id,
                'name': program.name,
                'description': program.description,
                'created_at': program.created_at,
                'updated_at': program.updated_at
            }
            for program in self.saved_programs.values()
        ]
            for program in self.saved_programs.values()
        ]
