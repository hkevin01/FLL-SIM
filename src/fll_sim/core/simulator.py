"""
Main simulation engine for FLL-Sim.

This module contains the core Simulator class that orchestrates the entire
simulation environment including physics, rendering, and game logic.
"""

import time
from typing import Optional, List, Callable
import pygame
import pymunk
import pymunk.pygame_util
from dataclasses import dataclass

from ..robot.robot import Robot
from ..environment.game_map import GameMap
from ..visualization.renderer import Renderer


@dataclass
class SimulationConfig:
    """Configuration settings for the simulation."""
    
    # Physics settings
    physics_fps: int = 60
    physics_dt: float = 1.0 / 60.0
    gravity: tuple = (0, 0)  # No gravity for top-down 2D simulation
    
    # Rendering settings
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60
    
    # Game settings
    real_time_factor: float = 1.0  # 1.0 = real time, 0.5 = half speed, 2.0 = double speed
    
    # Debug settings
    show_debug_info: bool = False
    show_physics_debug: bool = False


class Simulator:
    """
    Main simulation engine that manages the robot, environment, and physics.
    
    The Simulator coordinates all aspects of the FLL simulation including:
    - Physics simulation using Pymunk
    - Robot behavior and control
    - Environment interactions
    - Mission scoring
    - Real-time visualization
    """
    
    def __init__(self, robot: Robot, game_map: GameMap, config: Optional[SimulationConfig] = None):
        """
        Initialize the simulator.
        
        Args:
            robot: The robot to simulate
            game_map: The game map/environment
            config: Simulation configuration settings
        """
        self.robot = robot
        self.game_map = game_map
        self.config = config or SimulationConfig()
        
        # Initialize physics
        self.space = pymunk.Space()
        self.space.gravity = self.config.gravity
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))
        pygame.display.set_caption("FLL-Sim - First Lego League Simulator")
        self.clock = pygame.time.Clock()
        
        # Initialize renderer
        self.renderer = Renderer(self.screen, self.space)
        
        # Simulation state
        self.running = False
        self.paused = False
        self.simulation_time = 0.0
        self.frame_count = 0
        
        # Event callbacks
        self.on_mission_complete: List[Callable] = []
        self.on_collision: List[Callable] = []
        
        # Setup simulation
        self._setup_physics()
        self._setup_input_handlers()
    
    def _setup_physics(self):
        """Setup the physics world with robot and environment."""
        # Add robot to physics space
        self.robot.add_to_space(self.space)
        
        # Add game map obstacles to physics space
        self.game_map.add_to_space(self.space)
        
        # Setup collision handlers
        self._setup_collision_handlers()
    
    def _setup_collision_handlers(self):
        """Setup collision detection between robot and environment."""
        def robot_obstacle_collision(arbiter, space, data):
            """Handle collision between robot and obstacles."""
            for callback in self.on_collision:
                callback(arbiter, space, data)
            return True
        
        # Robot-obstacle collision
        handler = self.space.add_collision_handler(
            self.robot.collision_type, 
            self.game_map.obstacle_collision_type
        )
        handler.begin = robot_obstacle_collision
    
    def _setup_input_handlers(self):
        """Setup keyboard and mouse input handlers."""
        self.key_handlers = {
            pygame.K_SPACE: self.toggle_pause,
            pygame.K_r: self.reset_simulation,
            pygame.K_q: self.stop,
            pygame.K_d: self.toggle_debug,
        }
    
    def start(self):
        """Start the simulation loop."""
        self.running = True
        self._simulation_loop()
    
    def stop(self):
        """Stop the simulation."""
        self.running = False
    
    def pause(self):
        """Pause the simulation."""
        self.paused = True
    
    def resume(self):
        """Resume the simulation."""
        self.paused = False
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
    
    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.simulation_time = 0.0
        self.frame_count = 0
        self.robot.reset()
        self.game_map.reset()
    
    def toggle_debug(self):
        """Toggle debug visualization."""
        self.config.show_debug_info = not self.config.show_debug_info
        self.config.show_physics_debug = not self.config.show_physics_debug
    
    def step(self, dt: Optional[float] = None):
        """
        Step the simulation forward by one time step.
        
        Args:
            dt: Time delta in seconds. If None, uses config default.
        """
        if dt is None:
            dt = self.config.physics_dt
        
        # Update robot
        self.robot.update(dt)
        
        # Update game map (missions, animations, etc.)
        self.game_map.update(dt)
        
        # Step physics
        self.space.step(dt)
        
        # Update simulation time
        self.simulation_time += dt
        self.frame_count += 1
    
    def _simulation_loop(self):
        """Main simulation loop."""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            real_dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            self._handle_events()
            
            # Update simulation if not paused
            if not self.paused:
                # Apply real-time factor
                sim_dt = real_dt * self.config.real_time_factor
                self.step(sim_dt)
            
            # Render
            self._render()
            
            # Control frame rate
            self.clock.tick(self.config.fps)
        
        # Cleanup
        pygame.quit()
    
    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_handlers:
                    self.key_handlers[event.key]()
                else:
                    # Pass other keys to robot for manual control
                    self.robot.handle_key_event(event)
            
            elif event.type == pygame.KEYUP:
                self.robot.handle_key_event(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events."""
        if event.button == 1:  # Left click
            # Convert screen coordinates to world coordinates
            world_pos = self.renderer.screen_to_world(event.pos)
            print(f"Clicked at world position: {world_pos}")
    
    def _render(self):
        """Render the current simulation frame."""
        # Clear screen
        self.screen.fill((50, 50, 50))  # Dark gray background
        
        # Render game map
        self.game_map.render(self.renderer)
        
        # Render robot
        self.robot.render(self.renderer)
        
        # Render debug info if enabled
        if self.config.show_debug_info:
            self._render_debug_info()
        
        if self.config.show_physics_debug:
            self._render_physics_debug()
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self):
        """Render debug information overlay."""
        font = pygame.font.Font(None, 24)
        debug_info = [
            f"Time: {self.simulation_time:.2f}s",
            f"Frame: {self.frame_count}",
            f"FPS: {self.clock.get_fps():.1f}",
            f"Robot Position: ({self.robot.x:.1f}, {self.robot.y:.1f})",
            f"Robot Angle: {self.robot.angle:.1f}°",
            f"Paused: {self.paused}",
        ]
        
        y_offset = 10
        for info in debug_info:
            text_surface = font.render(info, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def _render_physics_debug(self):
        """Render physics debug visualization."""
        debug_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(debug_options)
    
    def add_mission_callback(self, callback: Callable):
        """Add a callback for when missions are completed."""
        self.on_mission_complete.append(callback)
    
    def add_collision_callback(self, callback: Callable):
        """Add a callback for collision events."""
        self.on_collision.append(callback)
    
    def get_simulation_state(self) -> dict:
        """Get current simulation state for debugging or analysis."""
        return {
            "time": self.simulation_time,
            "frame": self.frame_count,
            "robot": self.robot.get_state(),
            "missions": self.game_map.get_mission_states(),
            "paused": self.paused,
            "running": self.running,
        }
