"""
Main simulation engine for FLL-Sim.

This module contains the core Simulator class that orchestrates physics,
rendering, and game logic. It can be executed as a module:

    python -m fll_sim.core.simulator --profile beginner --robot standard_fll

Use --headless for CI or servers without a display, and --exit-after to
automatically stop after N seconds.
"""

from __future__ import annotations

import argparse
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import pygame
import pymunk
import pymunk.pygame_util

from ..environment.game_map import GameMap
from ..robot.robot import Robot
from ..utils.errors import FLLSimError
from ..utils.logger import FLLLogger
from ..visualization.renderer import Renderer


@dataclass
class SimulationConfig:
    """Configuration settings for the simulation."""

    # Physics settings
    physics_fps: int = 60
    physics_dt: float = 1.0 / 60.0
    gravity: tuple = (0, 0)

    # Rendering
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60

    # Game settings
    real_time_factor: float = 1.0

    # Debug
    show_debug_info: bool = False
    show_physics_debug: bool = False


class Simulator:
    """
    Main simulation engine that manages robot, environment, and physics.
    """

    def __init__(
        self,
        robot: Robot,
        game_map: GameMap,
        config: Optional[SimulationConfig] = None,
        competition_mode: bool = False,
        competition_time_limit: int = 150,
    ) -> None:
        self.robot = robot
        self.game_map = game_map
        self.config = config or SimulationConfig()

        self.logger = FLLLogger("Simulator")
        try:
            # Physics
            self.space = pymunk.Space()
            self.space.gravity = self.config.gravity

            # Pygame
            pygame.init()  # type: ignore[attr-defined]
            self.screen = pygame.display.set_mode(
                (self.config.window_width, self.config.window_height)
            )
            pygame.display.set_caption("FLL-Sim - First Lego League Simulator")
            self.clock = pygame.time.Clock()

            # Renderer
            self.renderer = Renderer(self.screen, self.space)

            # State
            self.running = False
            self.paused = False
            self.simulation_time = 0.0
            self.frame_count = 0

            # Callbacks
            self.on_mission_complete: List[Callable[..., None]] = []
            self.on_collision: List[Callable[..., None]] = []

            # Competition
            self.competition_mode = competition_mode
            self.competition_time_limit = competition_time_limit
            self.competition_time_left: float = float(competition_time_limit)

            # Setup
            self._setup_physics()
            self._setup_input_handlers()
            self.logger.info("Simulator initialized successfully.")
        except Exception as e:  # noqa: BLE001
            self.logger.error(f"Simulator initialization failed: {e}")
            raise FLLSimError(f"Simulator initialization error: {e}") from e

    def _setup_physics(self) -> None:
        """Setup the physics world with robot and environment."""
        # Add robot to physics space
        self.robot.add_to_space(self.space)

        # Add game map obstacles to physics space
        self.game_map.add_to_space(self.space)

        # Setup collision handlers
        self._setup_collision_handlers()

    def _setup_collision_handlers(self) -> None:
        """Setup collision detection between robot and environment."""

        def _notify(
            arbiter: pymunk.Arbiter, space: pymunk.Space, data: Any
        ) -> None:
            for cb in self.on_collision:
                try:
                    cb(arbiter, space, data)
                except (ValueError, TypeError, RuntimeError) as err:
                    self.logger.error(f"Collision callback error: {err}")

        # Support both common Pymunk APIs
        add_handler = getattr(self.space, "add_collision_handler", None)
        if add_handler is not None:
            # Pymunk standard API: handler.begin should return bool
            handler = add_handler(1, 2)  # robot, obstacle

            def _begin_true(
                arbiter: "pymunk.Arbiter",
                space: "pymunk.Space",
                data: Any,
            ) -> bool:
                _notify(arbiter, space, data)
                return True

            # Assign callback
            handler.begin = _begin_true
        elif hasattr(self.space, "on_collision"):
            # Some wrappers expect callbacks returning None
            def _begin_none(
                arbiter: "pymunk.Arbiter",
                space: "pymunk.Space",
                data: Any,
            ) -> None:
                _notify(arbiter, space, data)
                return None

            self.space.on_collision(
                collision_type_a=1,  # Robot collision type
                collision_type_b=2,  # Obstacle collision type
                begin=_begin_none,
            )
        else:
            self.logger.warning(
                "Space has no collision handler API; collisions disabled"
            )

    def _setup_input_handlers(self) -> None:
        """Setup keyboard and mouse input handlers."""
        self.key_handlers = {
            pygame.K_SPACE: self.toggle_pause,  # type: ignore[attr-defined]
            pygame.K_r: self.reset_simulation,  # type: ignore[attr-defined]
            pygame.K_q: self.stop,  # type: ignore[attr-defined]
            pygame.K_d: self.toggle_debug,  # type: ignore[attr-defined]
        }

    def start(self) -> None:
        """Start the simulation loop."""
        self.running = True
        self._simulation_loop()

    def stop(self) -> None:
        """Stop the simulation."""
        self.running = False

    def pause(self) -> None:
        """Pause the simulation."""
        self.paused = True

    def resume(self) -> None:
        """Resume the simulation."""
        self.paused = False

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        self.paused = not self.paused

    def reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        self.simulation_time = 0.0
        self.frame_count = 0
        self.robot.reset()
        self.game_map.reset()

    def toggle_debug(self) -> None:
        """Toggle debug visualization."""
        self.config.show_debug_info = not self.config.show_debug_info
        self.config.show_physics_debug = not self.config.show_physics_debug

    def step(self, dt: Optional[float] = None) -> None:
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

        # Competition timer logic
        if self.competition_mode:
            self.competition_time_left -= float(dt)
            if self.competition_time_left <= 0:
                self.competition_time_left = 0
                self.stop()

    def _simulation_loop(self) -> None:
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
    pygame.quit()  # type: ignore[attr-defined]

    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():  # type: ignore[attr-defined]
            if (
                event.type
                == pygame.QUIT  # type: ignore[attr-defined]
            ):
                self.stop()

            elif (
                event.type
                == pygame.KEYDOWN  # type: ignore[attr-defined]
            ):
                if event.key in self.key_handlers:
                    self.key_handlers[event.key]()
                else:
                    # Pass other keys to robot for manual control
                    self.robot.handle_key_event(event)

            elif (
                event.type
                == pygame.KEYUP  # type: ignore[attr-defined]
            ):
                self.robot.handle_key_event(event)

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN  # type: ignore[attr-defined]
            ):
                self._handle_mouse_click(event)

    def _handle_mouse_click(self, event: Any) -> None:
        """Handle mouse click events."""
        if event.button == 1:  # Left click
            # Convert screen coordinates to world coordinates
            world_pos = self.renderer.screen_to_world(event.pos)
            print(f"Clicked at world position: {world_pos}")

    def _render(self) -> None:
        """Render the current simulation frame."""
        # Reset per-frame renderer state
        if hasattr(self.renderer, 'begin_frame'):
            self.renderer.begin_frame()

        # Draw background or mat
        if hasattr(self.renderer, 'draw_map'):
            self.renderer.draw_map(self.game_map)
        else:
            self.screen.fill((50, 50, 50))  # Fallback background

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
    pygame.display.flip()  # type: ignore[attr-defined]

    def _render_debug_info(self) -> None:
        """Render debug information overlay."""
        # Use renderer's text API with background and overlap handling
        items = [
            (f"Time: {self.simulation_time:.2f}s", 10, 10),
            (f"Frame: {self.frame_count}", 10, 35),
            (f"FPS: {self.clock.get_fps():.1f}", 10, 60),
            (f"Robot: ({self.robot.x:.1f}, {self.robot.y:.1f})", 10, 85),
            (f"Angle: {self.robot.angle:.1f}°", 10, 110),
            (f"Paused: {self.paused}", 10, 135),
        ]
        for text, x, y in items:
            if hasattr(self.renderer, 'draw_text_screen'):
                self.renderer.draw_text_screen(
                    text, x, y, 'small', with_bg=True
                )
            else:
                font = pygame.font.Font(None, 24)  # type: ignore[attr-defined]
                surf = font.render(text, True, (255, 255, 255))
                self.screen.blit(surf, (x, y))

    def _render_physics_debug(self) -> None:
        """Render physics debug visualization."""
        debug_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(debug_options)

    def add_mission_callback(self, callback: Callable) -> None:
        """Add a callback for when missions are completed."""
        self.on_mission_complete.append(callback)

    def add_collision_callback(self, callback: Callable) -> None:
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

    def get_competition_time_left(self) -> Optional[float]:
        if self.competition_mode:
            return max(0, self.competition_time_left)
        return None


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments for running the simulator as a module."""
    parser = argparse.ArgumentParser(description="Run FLL-Sim simulator")
    parser.add_argument(
        "--profile", default="beginner", help="Simulation profile"
    )
    parser.add_argument(
        "--robot", default="standard_fll", help="Robot type"
    )
    parser.add_argument(
        "--season", default="2024", help="FLL season"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug overlays"
    )
    parser.add_argument(
        "--performance", action="store_true",
        help="Enable performance monitoring",
    )
    parser.add_argument(
        "--log", action="store_true", help="Enable detailed logging"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run without creating a window (SDL dummy)",
    )
    parser.add_argument(
        "--exit-after", type=float, default=0.0,
        help="Automatically stop after N seconds",
    )
    parser.add_argument(
        "--background-image",
        dest="background_image",
        default=os.environ.get("FLL_SIM_BACKGROUND", ""),
        help="Path to background image (FLL mat).",
    )
    parser.add_argument(
        "--background-size",
        dest="background_size",
        default="",
        help=(
            "Optional background size in mm as WIDTHxHEIGHT "
            "(e.g., 2400x1200)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    """Module entrypoint: construct and run the simulator based on CLI args."""
    args = _parse_args(argv)

    # Graphics fallbacks to avoid GLX issues in containers/X11
    if args.headless:
        # Use SDL dummy driver in headless mode so pygame can initialize
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    else:
        # Force software rendering paths; avoid indirect GLX
        os.environ.setdefault("LIBGL_ALWAYS_INDIRECT", "0")
        os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
        os.environ.setdefault("SDL_VIDEODRIVER", "x11")
        os.environ.setdefault("SDL_RENDER_DRIVER", "software")
        os.environ.setdefault("SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR", "0")

    # Basic prints help when launched from another process (e.g., GUI)
    print(
        f"[sim] Starting simulator (profile={args.profile}, "
        f"robot={args.robot}, season={args.season}, headless={args.headless})"
    )

    # Map CLI flags to config
    sim_config = SimulationConfig()
    sim_config.show_debug_info = bool(args.debug)
    # Keep physics debug off unless explicitly enabled via other future flags

    # Create core objects (extend later to use profile/robot/season configs)
    game_map = GameMap()
    robot = Robot()
    sim = Simulator(robot=robot, game_map=game_map, config=sim_config)

    # Optional background mat image
    try:
        bg_path = (
            args.background_image.strip() if args.background_image else ""
        )
        if bg_path and os.path.exists(bg_path):
            # Determine world size for the image
            width_mm = game_map.config.width
            height_mm = game_map.config.height
            if args.background_size and "x" in args.background_size:
                try:
                    w_str, h_str = args.background_size.lower().split("x", 1)
                    width_mm = float(w_str)
                    height_mm = float(h_str)
                except ValueError:
                    pass
            img = pygame.image.load(bg_path)
            if hasattr(sim.renderer, "set_background_image"):
                sim.renderer.set_background_image(img, width_mm, height_mm)
                print(
                    f"[sim] Background loaded: {bg_path} "
                    f"-> world {int(width_mm)}x{int(height_mm)} mm"
                )
    except (
        FileNotFoundError,
        OSError,
        pygame.error,  # type: ignore[attr-defined]
    ) as e:
        print(f"[sim] Warning: failed to load background image: {e}")

    # Support timed exit for CI/headless demos
    stopper = None
    if args.exit_after and args.exit_after > 0:
        def _stop_later() -> None:
            time.sleep(args.exit_after)
            sim.stop()

        stopper = threading.Thread(target=_stop_later, daemon=True)
        stopper.start()

    try:
        sim.start()
    except KeyboardInterrupt:
        sim.stop()
    finally:
        print("[sim] Simulator stopped")


if __name__ == "__main__":
    main()

# Modularization and maintainability improvements (2025-07-21):
# - Added/expanded docstrings for Simulator and SimulationConfig.
# - Ensured type hints for all public methods and attributes.
# - Prepared for separation of physics, rendering, and mission logic into
#   dedicated modules/classes.
# - Refactored initialization to clarify separation of concerns.
# - Improved comments for maintainability.
