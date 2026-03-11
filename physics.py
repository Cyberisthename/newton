"""
Desktop Newton - Physics Module
Handles ragdoll construction and Pymunk physics simulation.
"""
import pymunk
import pymunk.pygame_util
import pygame
import math


class RagdollPart:
    """Base class for ragdoll body parts."""
    
    def __init__(self, body, shape, name, color):
        self.body = body
        self.shape = shape
        self.name = name
        self.color = color
        self.shape.color = color
        self.shape.friction = 0.5
        self.shape.elasticity = 0.3
        
    def get_position(self):
        return self.body.position
    
    def get_angle(self):
        return self.body.angle


class Ragdoll:
    """
    A physics-based ragdoll composed of multiple connected body parts.
    Uses Pymunk for rigid body dynamics.
    """
    
    COLORS = {
        'head': (255, 200, 150),
        'torso': (100, 150, 200),
        'arm': (150, 200, 100),
        'leg': (200, 100, 150),
        'joint': (255, 255, 255)
    }
    
    def __init__(self, space, position=(400, 300), scale=1.0):
        self.space = space
        self.scale = scale
        self.parts = []
        self.joints = []
        self.constraints = []
        
        # Build the ragdoll
        self._build_ragdoll(position)
        
    def _build_ragdoll(self, start_pos):
        """Construct the ragdoll from body parts connected by joints."""
        x, y = start_pos
        s = self.scale
        
        # Head (circle)
        head_radius = 15 * s
        head_mass = 3.0
        head_moment = pymunk.moment_for_circle(head_mass, 0, head_radius)
        head_body = pymunk.Body(head_mass, head_moment)
        head_body.position = (x, y - 60 * s)
        head_shape = pymunk.Circle(head_body, head_radius)
        head_part = RagdollPart(head_body, head_shape, 'head', self.COLORS['head'])
        self.parts.append(head_part)
        self.space.add(head_body, head_shape)
        
        # Torso (box/rectangle)
        torso_width = 20 * s
        torso_height = 40 * s
        torso_mass = 10.0
        torso_moment = pymunk.moment_for_box(torso_mass, (torso_width, torso_height))
        torso_body = pymunk.Body(torso_mass, torso_moment)
        torso_body.position = (x, y - 20 * s)
        torso_shape = pymunk.Poly.create_box(torso_body, (torso_width, torso_height))
        torso_part = RagdollPart(torso_body, torso_shape, 'torso', self.COLORS['torso'])
        self.parts.append(torso_part)
        self.space.add(torso_body, torso_shape)
        
        # Head-Torso connection (neck)
        neck_joint = pymunk.PivotJoint(head_body, torso_body, (x, y - 40 * s))
        neck_limit = pymunk.RotaryLimitJoint(head_body, torso_body, -0.5, 0.5)
        self.joints.append(neck_joint)
        self.joints.append(neck_limit)
        self.space.add(neck_joint, neck_limit)
        
        # Arms
        self._create_limb(x, y - 40 * s, 'left_arm', -1)
        self._create_limb(x, y - 40 * s, 'right_arm', 1)
        
        # Legs
        self._create_leg(x, y, 'left_leg', -1)
        self._create_leg(x, y, 'right_leg', 1)
        
    def _create_limb(self, x, y, side, direction):
        """Create an arm (upper + forearm)."""
        s = self.scale
        
        # Upper arm
        upper_arm_width = 8 * s
        upper_arm_height = 25 * s
        upper_mass = 2.5
        upper_moment = pymunk.moment_for_box(upper_mass, (upper_arm_width, upper_arm_height))
        upper_body = pymunk.Body(upper_mass, upper_moment)
        upper_body.position = (x + direction * 20 * s, y - 5 * s)
        upper_shape = pymunk.Poly.create_box(upper_body, (upper_arm_width, upper_arm_height))
        upper_part = RagdollPart(upper_body, upper_shape, f'{side}_upper', self.COLORS['arm'])
        self.parts.append(upper_part)
        self.space.add(upper_body, upper_shape)
        
        # Connect to torso at shoulder
        shoulder_joint = pymunk.PivotJoint(
            self.parts[1].body,  # Torso
            upper_body,
            (x + direction * 15 * s, y - 5 * s)
        )
        shoulder_limit = pymunk.RotaryLimitJoint(
            self.parts[1].body, upper_body,
            -1.0, 1.5 if direction > 0 else -1.5
        )
        self.joints.append(shoulder_joint)
        self.joints.append(shoulder_limit)
        self.space.add(shoulder_joint, shoulder_limit)
        
        # Forearm
        forearm_width = 7 * s
        forearm_height = 22 * s
        forearm_mass = 2.0
        forearm_moment = pymunk.moment_for_box(forearm_mass, (forearm_width, forearm_height))
        forearm_body = pymunk.Body(forearm_mass, forearm_moment)
        forearm_body.position = (x + direction * 20 * s, y - 35 * s)
        forearm_shape = pymunk.Poly.create_box(forearm_body, (forearm_width, forearm_height))
        forearm_part = RagdollPart(forearm_body, forearm_shape, f'{side}_forearm', self.COLORS['arm'])
        self.parts.append(forearm_part)
        self.space.add(forearm_body, forearm_shape)
        
        # Elbow
        elbow_joint = pymunk.PivotJoint(
            upper_body, forearm_body,
            (x + direction * 20 * s, y - 20 * s)
        )
        elbow_limit = pymunk.RotaryLimitJoint(
            upper_body, forearm_body,
            -2.5, 0.0
        )
        self.joints.append(elbow_joint)
        self.joints.append(elbow_limit)
        self.space.add(elbow_joint, elbow_limit)
        
    def _create_leg(self, x, y, side, direction):
        """Create a leg (thigh + calf)."""
        s = self.scale
        
        # Thigh
        thigh_width = 10 * s
        thigh_height = 30 * s
        thigh_mass = 4.0
        thigh_moment = pymunk.moment_for_box(thigh_mass, (thigh_width, thigh_height))
        thigh_body = pymunk.Body(thigh_mass, thigh_moment)
        thigh_body.position = (x + direction * 10 * s, y + 35 * s)
        thigh_shape = pymunk.Poly.create_box(thigh_body, (thigh_width, thigh_height))
        thigh_part = RagdollPart(thigh_body, thigh_shape, f'{side}_thigh', self.COLORS['leg'])
        self.parts.append(thigh_part)
        self.space.add(thigh_body, thigh_shape)
        
        # Connect to torso at hip
        hip_joint = pymunk.PivotJoint(
            self.parts[1].body,  # Torso
            thigh_body,
            (x + direction * 10 * s, y + 10 * s)
        )
        hip_limit = pymunk.RotaryLimitJoint(
            self.parts[1].body, thigh_body,
            -1.0, 0.5
        )
        self.joints.append(hip_joint)
        self.joints.append(hip_limit)
        self.space.add(hip_joint, hip_limit)
        
        # Calf
        calf_width = 8 * s
        calf_height = 28 * s
        calf_mass = 3.0
        calf_moment = pymunk.moment_for_box(calf_mass, (calf_width, calf_height))
        calf_body = pymunk.Body(calf_mass, calf_moment)
        calf_body.position = (x + direction * 10 * s, y + 65 * s)
        calf_shape = pymunk.Poly.create_box(calf_body, (calf_width, calf_height))
        calf_part = RagdollPart(calf_body, calf_shape, f'{side}_calf', self.COLORS['leg'])
        self.parts.append(calf_part)
        self.space.add(calf_body, calf_shape)
        
        # Knee
        knee_joint = pymunk.PivotJoint(
            thigh_body, calf_body,
            (x + direction * 10 * s, y + 50 * s)
        )
        knee_limit = pymunk.RotaryLimitJoint(
            thigh_body, calf_body,
            0.0, 2.0
        )
        self.joints.append(knee_joint)
        self.joints.append(knee_limit)
        self.space.add(knee_joint, knee_limit)
        
    def get_part_at_point(self, point):
        """Get the body part at the given screen coordinates."""
        query = self.space.point_query_nearest(point, 0, pymunk.ShapeFilter())
        if query and query.shape:
            for part in self.parts:
                if part.shape == query.shape:
                    return part
        return None
    
    def apply_force_to_part(self, part_name, force):
        """Apply a force to a named body part."""
        for part in self.parts:
            if part.name == part_name:
                part.body.apply_force_at_local_point(force, (0, 0))
                break
    
    def set_color(self, color_type, color):
        """Set the color of a specific body part type."""
        self.COLORS[color_type] = color
        for part in self.parts:
            if color_type in part.name or (color_type == 'torso' and part.name == 'torso'):
                part.color = color
                part.shape.color = color
                
    def destroy(self):
        """Remove all ragdoll parts from the physics space."""
        for joint in self.joints:
            self.space.remove(joint)
        for part in self.parts:
            self.space.remove(part.body, part.shape)
        self.joints.clear()
        self.parts.clear()
        
    def update_scale(self, new_scale, position):
        """Rebuild the ragdoll with a new scale."""
        self.destroy()
        self.scale = new_scale
        self._build_ragdoll(position)


class PhysicsWorld:
    """Manages the Pymunk physics simulation."""
    
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Gravity pointing down
        self.space.damping = 0.9  # Air resistance
        self.space.collision_slop = 0.1
        
        # Create floor
        self._create_floor()
        
        # Create walls (invisible screen boundaries)
        self._create_walls()
        
        # Ragdoll
        self.ragdoll = None
        
        # Mouse drag constraint
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.mouse_joint = None
        
    def _create_floor(self):
        """Create an invisible floor at the bottom of the screen."""
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, (0, 2000), (2000, 2000), 10)
        floor_shape.friction = 0.8
        floor_shape.elasticity = 0.2
        self.space.add(floor_body, floor_shape)
        self.floor = floor_body
        
    def _create_walls(self):
        """Create invisible walls to keep ragdoll on screen."""
        wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        # Left wall
        left = pymunk.Segment(wall_body, (-50, 0), (-50, 2000), 10)
        # Right wall  
        right = pymunk.Segment(wall_body, (2050, 0), (2050, 2000), 10)
        # Top wall
        top = pymunk.Segment(wall_body, (0, -50), (2000, -50), 10)
        
        for wall in [left, right, top]:
            wall.friction = 0.5
            wall.elasticity = 0.5
            
        self.space.add(wall_body, left, right, top)
        self.walls = wall_body
        
    def create_ragdoll(self, position=(400, 300), scale=1.0):
        """Create a new ragdoll at the specified position."""
        if self.ragdoll:
            self.ragdoll.destroy()
        self.ragdoll = Ragdoll(self.space, position, scale)
        return self.ragdoll
        
    def step(self, dt):
        """Advance the physics simulation."""
        # Use a fixed time step for stability
        self.space.step(1/60.0)
        
    def start_drag(self, position):
        """Start dragging a ragdoll part at the given position."""
        if not self.ragdoll:
            return None
            
        part = self.ragdoll.get_part_at_point(position)
        if part:
            self.mouse_body.position = position
            self.mouse_joint = pymunk.PivotJoint(
                self.mouse_body, part.body, (0, 0), part.body.world_to_local(position)
            )
            self.mouse_joint.max_force = 50000
            self.mouse_joint.error_bias = 0.1
            self.space.add(self.mouse_joint)
            return part
        return None
        
    def update_drag(self, position):
        """Update the drag position."""
        if self.mouse_joint:
            self.mouse_body.position = position
            
    def end_drag(self):
        """End the current drag operation."""
        if self.mouse_joint:
            self.space.remove(self.mouse_joint)
            self.mouse_joint = None
            
    def set_gravity(self, gravity):
        """Set the gravity vector."""
        self.space.gravity = (0, gravity)
        
    def set_damping(self, damping):
        """Set the global damping (air resistance)."""
        self.space.damping = damping
        
    def set_elasticity(self, elasticity):
        """Set the elasticity (bounciness) of all ragdoll parts."""
        if self.ragdoll:
            for part in self.ragdoll.parts:
                part.shape.elasticity = elasticity
                
    def set_friction(self, friction):
        """Set the friction of all ragdoll parts."""
        if self.ragdoll:
            for part in self.ragdoll.parts:
                part.shape.friction = friction
