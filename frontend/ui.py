import pygame
import pygame.freetype
import math

# Enhanced UI Colors with a vibrant, trendy palette
WHITE = (255, 255, 255)
BLACK = (30, 30, 35)  # Deep, soft black
GRAY = (200, 200, 200)
LIGHT_GRAY = (245, 245, 250)  # Very light gray with a hint of purple
DARK_GRAY = (75, 80, 95)  # Cool-toned dark gray

# Modern color palette with vibrant colors for Gen Z and Gen Alpha appeal
PRIMARY = (79, 93, 247)  # Vibrant blue-purple
PRIMARY_LIGHT = (141, 155, 255)  # Lighter version of primary
PRIMARY_DARK = (53, 64, 196)  # Darker version of primary
SECONDARY = (0, 184, 148)  # Bright teal
ACCENT = (255, 107, 107)  # Coral red
ACCENT_ALT = (255, 159, 67)  # Bright orange
POP_PURPLE = (162, 94, 245)  # Vibrant purple
POP_PINK = (255, 118, 196)  # Bright pink
POP_YELLOW = (253, 203, 76)  # Bright yellow
ERROR = (255, 84, 84)  # Bright red for errors
SUCCESS = (0, 204, 136)  # Bright green for success messages
WARNING = (255, 177, 66)  # Bright orange for warnings

# Legacy colors for backward compatibility
BLUE = PRIMARY
LIGHT_BLUE = PRIMARY_LIGHT
RED = ERROR
GREEN = SUCCESS
YELLOW = POP_YELLOW

# For gradient backgrounds
GRADIENT_TOP = (232, 237, 255)  # Light purple-blue
GRADIENT_BOTTOM = (245, 245, 255)  # Almost white with a hint of purple

# UI Element styles - increased radius for more modern look
BUTTON_RADIUS = 16  # More rounded corners for buttons
PANEL_RADIUS = 20  # More rounded corners for panels
SHADOW_COLOR = (0, 0, 0, 40)  # Slightly darker transparent black for shadows

class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=PRIMARY_DARK, 
                text_color=None, visible=True, font_size=28, align="center", icon=None):
        # Create rect based on alignment
        if align == "center":
            self.rect = pygame.Rect(x - width//2, y, width, height)
        elif align == "right":
            self.rect = pygame.Rect(x - width, y, width, height)
        else:  # left alignment
            self.rect = pygame.Rect(x, y, width, height)
            
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.visible = visible
        self.hovered = False
        self.disabled = False
        self.font = pygame.font.Font(None, font_size)
        self.font_size = font_size
        self.border_radius = BUTTON_RADIUS
        self.animation_state = 0
        self.pulse_direction = 1
        self.shadow_offset = 4
        self.custom_text = False
        self.align = align
        self.icon = icon  # Optional icon to display next to text
        
        # New: Enhanced button styling
        self.padding = {
            'top': 10,
            'bottom': 10,
            'left': 20,
            'right': 20
        }
        
        # New: Animation properties
        self.hover_scale = 1.05
        self.click_scale = 0.95
        self.animation_speed = 0.1
        self.click_animation = 0
        self.last_click_time = 0
        
        # New: Gradient properties
        self.use_gradient = True
        self.gradient_top = (255, 255, 255, 50)
        self.gradient_bottom = (0, 0, 0, 0)
        
    def draw(self, screen):
        if not self.visible:
            return
            
        # Update animation states
        current_time = pygame.time.get_ticks()
        
        # Hover animation
        if self.hovered and not self.disabled:
            self.animation_state = min(1.0, self.animation_state + self.animation_speed)
        else:
            self.animation_state = max(0.0, self.animation_state - self.animation_speed)
            
        # Click animation
        if current_time - self.last_click_time < 200:  # 200ms click animation
            self.click_animation = 1.0 - ((current_time - self.last_click_time) / 200)
        else:
            self.click_animation = 0
            
        # Calculate current scale
        scale = 1.0
        if not self.disabled:
            scale = 1.0 + (self.hover_scale - 1.0) * self.animation_state
            scale *= 1.0 - (1.0 - self.click_scale) * self.click_animation
            
        # Calculate current color
        base_color = LIGHT_GRAY if self.disabled else self.color
        hover_color = LIGHT_GRAY if self.disabled else self.hover_color
        
        r = int(base_color[0] + (hover_color[0] - base_color[0]) * self.animation_state)
        g = int(base_color[1] + (hover_color[1] - base_color[1]) * self.animation_state)
        b = int(base_color[2] + (hover_color[2] - base_color[2]) * self.animation_state)
        current_color = (r, g, b)
        
        # Draw shadow with scale
        if not self.disabled:
            shadow_rect = pygame.Rect(
                self.rect.x + self.shadow_offset,
                self.rect.y + self.shadow_offset,
                self.rect.width * scale,
                self.rect.height * scale
            )
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, SHADOW_COLOR, 
                            pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                            border_radius=self.border_radius)
            screen.blit(pygame.transform.scale(shadow_surface, 
                            (int(self.rect.width * scale), int(self.rect.height * scale))), 
                            shadow_rect)
        
        # Draw button with scale
        scaled_rect = pygame.Rect(
            self.rect.x + (self.rect.width * (1 - scale)) / 2,
            self.rect.y + (self.rect.height * (1 - scale)) / 2,
            self.rect.width * scale,
            self.rect.height * scale
        )
        pygame.draw.rect(screen, current_color, scaled_rect, border_radius=self.border_radius)
        
        # Add gradient effect
        if self.use_gradient and not self.disabled:
            gradient_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            for i in range(self.rect.height):
                alpha = int(50 * (1 - i / self.rect.height))
                color = (
                    int(self.gradient_top[0] + (self.gradient_bottom[0] - self.gradient_top[0]) * (i / self.rect.height)),
                    int(self.gradient_top[1] + (self.gradient_bottom[1] - self.gradient_top[1]) * (i / self.rect.height)),
                    int(self.gradient_top[2] + (self.gradient_bottom[2] - self.gradient_top[2]) * (i / self.rect.height)),
                    alpha
                )
                pygame.draw.line(gradient_surface, color, (0, i), (self.rect.width, i))
            gradient_surface = pygame.transform.scale(gradient_surface, 
                            (int(self.rect.width * scale), int(self.rect.height * scale)))
            gradient_rect = gradient_surface.get_rect(topleft=scaled_rect.topleft)
            screen.blit(gradient_surface, gradient_rect)
        
        # Draw text with proper padding and scale
        if self.text:
            text_color = self.text_color if self.text_color else WHITE if self.is_dark_color(current_color) else BLACK
            
            # Add icon to text if provided
            display_text = self.text
            if self.icon:
                display_text = f"{self.icon} {self.text}"
            
            # Calculate text position with padding
            text_surface = self.font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=(
                scaled_rect.centerx,
                scaled_rect.centery
            ))
            
            # Add subtle text shadow for better readability
            shadow_surface = self.font.render(display_text, True, (0, 0, 0, 50))
            shadow_rect = shadow_surface.get_rect(center=(
                text_rect.centerx + 1,
                text_rect.centery + 1
            ))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
    
    def is_dark_color(self, color):
        # Improved algorithm to determine if a color is dark
        # Returns True if color is dark, meaning we should use white text
        r, g, b = color
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 140  # Slightly higher threshold for better contrast
        
    def update(self, mouse_pos):
        if not self.visible or self.disabled:
            self.hovered = False
            return
            
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos):
        result = self.visible and not self.disabled and self.rect.collidepoint(mouse_pos)
        if result:
            self.last_click_time = pygame.time.get_ticks()
        return result
        
    def set_disabled(self, disabled):
        self.disabled = disabled
        
    def set_position(self, x, y):
        """Update button position with proper alignment"""
        if self.align == "center":
            self.rect.x = x - self.rect.width//2
            self.rect.y = y
        elif self.align == "right":
            self.rect.x = x - self.rect.width
            self.rect.y = y
        else:  # left alignment
            self.rect.x = x
            self.rect.y = y

class TextBox:
    def __init__(self, x, y, width, height, placeholder="", multiline=False, max_length=None, 
                active_by_default=False, align="center", is_password=False):
        # Set position based on alignment
        if align == "center":
            self.rect = pygame.Rect(x - width//2, y, width, height)
        elif align == "right":
            self.rect = pygame.Rect(x - width, y, width, height)
        else:  # left alignment
            self.rect = pygame.Rect(x, y, width, height)
            
        self.text = ""
        self.placeholder = placeholder
        self.active = active_by_default
        self.font = pygame.font.SysFont("Arial", 24)
        self.multiline = multiline
        self.max_length = max_length
        self.visible = True
        self.align = align
        self.is_password = is_password  # New property for password fields
        
        # Enhanced styling properties
        self.border_radius = 8
        self.border_width = 2
        self.padding = {
            'top': 10,
            'bottom': 10,
            'left': 15,
            'right': 15
        }
        self.line_height = 30
        self.cursor_width = 2
        self.animation_state = 0
        self.focus_animation = 0
        self.shadow_offset = 3  # Added shadow offset for depth effect
        
        # Colors
        self.border_color = PRIMARY
        self.focus_border_color = PRIMARY_DARK
        self.background_color = WHITE
        self.text_color = BLACK
        self.placeholder_color = (150, 150, 150)
        
        # For multiline text boxes
        self.lines = [""]
        self.current_line = 0
        self.cursor_pos = 0
        
        # For single line text boxes
        self.cursor_pos_single = 0
        
        # For scrolling in multiline
        self.scroll_y = 0
        self.max_visible_lines = height // self.line_height
        
        # Add timestamp for cursor blinking
        self.last_cursor_toggle = pygame.time.get_ticks()
        self.cursor_visible = True
        
    def handle_event(self, event):
        if not self.visible:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on click
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            
            # If clicked inside, ensure cursor is visible immediately 
            if self.active:
                self.cursor_visible = True
                self.last_cursor_toggle = pygame.time.get_ticks()
            
            # Handle multiline cursor positioning
            if self.active and self.multiline and was_active:
                # Calculate which line was clicked
                rel_y = event.pos[1] - self.rect.y - 5 + self.scroll_y
                clicked_line = min(max(rel_y // self.line_height, 0), len(self.lines) - 1)
                self.current_line = clicked_line
                
                # Calculate cursor position within the line
                rel_x = event.pos[0] - self.rect.x - 5
                line = self.lines[self.current_line]
                
                # Find the closest character position based on x position
                self.cursor_pos = 0
                for i in range(len(line)):
                    test_surf = self.font.render(line[:i+1], True, BLACK)
                    char_width = test_surf.get_width()
                    if rel_x <= char_width:
                        self.cursor_pos = i
                        break
                    self.cursor_pos = len(line)
            
            # For single line text boxes, set cursor at appropriate position based on click
            elif self.active and not self.multiline:
                if self.text:
                    # Calculate cursor position within the text
                    rel_x = event.pos[0] - self.rect.x - 5
                    
                    # Find the closest character position based on x position
                    self.cursor_pos_single = 0
                    for i in range(len(self.text)):
                        test_surf = self.font.render(self.text[:i+1], True, BLACK)
                        char_width = test_surf.get_width()
                        if rel_x <= char_width:
                            self.cursor_pos_single = i
                            break
                        self.cursor_pos_single = len(self.text)
                else:
                    self.cursor_pos_single = 0
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.multiline:
                    if self.cursor_pos > 0:
                        # Delete character before cursor
                        self.lines[self.current_line] = (
                            self.lines[self.current_line][:self.cursor_pos-1] + 
                            self.lines[self.current_line][self.cursor_pos:]
                        )
                        self.cursor_pos -= 1
                    elif self.current_line > 0:
                        # Merge with previous line
                        self.cursor_pos = len(self.lines[self.current_line-1])
                        self.lines[self.current_line-1] += self.lines[self.current_line]
                        self.lines.pop(self.current_line)
                        self.current_line -= 1
                else:
                    # Handle single line backspace more intelligently
                    if self.cursor_pos_single > 0:
                        self.text = self.text[:self.cursor_pos_single-1] + self.text[self.cursor_pos_single:]
                        self.cursor_pos_single -= 1
            
            elif event.key == pygame.K_DELETE:
                # Delete character at cursor
                if self.multiline:
                    if self.cursor_pos < len(self.lines[self.current_line]):
                        self.lines[self.current_line] = (
                            self.lines[self.current_line][:self.cursor_pos] + 
                            self.lines[self.current_line][self.cursor_pos+1:]
                        )
                else:
                    if self.cursor_pos_single < len(self.text):
                        self.text = self.text[:self.cursor_pos_single] + self.text[self.cursor_pos_single+1:]
            
            elif event.key == pygame.K_LEFT:
                # Move cursor left
                if self.multiline:
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                    elif self.current_line > 0:
                        self.current_line -= 1
                        self.cursor_pos = len(self.lines[self.current_line])
                else:
                    self.cursor_pos_single = max(0, self.cursor_pos_single - 1)
            
            elif event.key == pygame.K_RIGHT:
                # Move cursor right
                if self.multiline:
                    if self.cursor_pos < len(self.lines[self.current_line]):
                        self.cursor_pos += 1
                    elif self.current_line < len(self.lines) - 1:
                        self.current_line += 1
                        self.cursor_pos = 0
                else:
                    self.cursor_pos_single = min(len(self.text), self.cursor_pos_single + 1)
            
            elif event.key == pygame.K_RETURN and self.multiline:
                # Insert new line
                new_line = self.lines[self.current_line][self.cursor_pos:]
                self.lines[self.current_line] = self.lines[self.current_line][:self.cursor_pos]
                self.lines.insert(self.current_line + 1, new_line)
                self.current_line += 1
                self.cursor_pos = 0
                
                # Scroll if needed
                if self.current_line >= self.max_visible_lines:
                    self.scroll_y += self.line_height
            
            elif event.key != pygame.K_TAB:  # Ignore tab key, but allow other keys including RETURN
                if self.max_length is None or (
                    self.multiline and sum(len(line) for line in self.lines) < self.max_length or
                    not self.multiline and len(self.text) < self.max_length
                ):
                    if self.multiline:
                        # Insert character at cursor position
                        self.lines[self.current_line] = (
                            self.lines[self.current_line][:self.cursor_pos] + 
                            event.unicode + 
                            self.lines[self.current_line][self.cursor_pos:]
                        )
                        self.cursor_pos += 1
                    else:
                        # Insert character at cursor position for single line
                        self.text = self.text[:self.cursor_pos_single] + event.unicode + self.text[self.cursor_pos_single:]
                        self.cursor_pos_single += 1
            
            # Reset cursor blink after any key press
            self.cursor_visible = True
            self.last_cursor_toggle = pygame.time.get_ticks()
            
            # Update scroll position for multiline textboxes
            if self.multiline:
                visible_start = self.scroll_y // self.line_height
                visible_end = visible_start + self.max_visible_lines - 1
                
                # Auto-scroll if cursor is outside visible area
                if self.current_line < visible_start:
                    self.scroll_y = max(0, self.current_line * self.line_height)
                elif self.current_line > visible_end:
                    self.scroll_y = (self.current_line - self.max_visible_lines + 1) * self.line_height
                    
    def get_text(self):
        """Get the full text content"""
        if self.multiline:
            return "\n".join(self.lines)
        return self.text
    
    def set_text(self, text):
        """Set the text content"""
        if self.multiline:
            self.lines = text.split("\n")
            if not self.lines:
                self.lines = [""]
            self.current_line = 0
            self.cursor_pos = 0
        else:
            self.text = text
            self.cursor_pos_single = len(text)
    
    def draw(self, screen):
        """Draw the text box."""
        if not self.visible:
            return
            
        # Draw shadow
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=self.border_radius)
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect, border_radius=self.border_radius)
        
        # Draw outline with animated width based on focus
        border_color = self.border_color
        if self.active:
            # Interpolate between border color and focus border color
            r = int(self.border_color[0] + (self.focus_border_color[0] - self.border_color[0]) * self.focus_animation)
            g = int(self.border_color[1] + (self.focus_border_color[1] - self.border_color[1]) * self.focus_animation)
            b = int(self.border_color[2] + (self.focus_border_color[2] - self.border_color[2]) * self.focus_animation)
            border_color = (r, g, b)
            
        # Calculate border width with animation
        animated_width = self.border_width + int(2 * self.focus_animation)
        pygame.draw.rect(screen, border_color, self.rect, 
                       animated_width, border_radius=self.border_radius)
        
        # Prepare for drawing text
        if self.multiline:
            # Handle multiline text drawing with scrolling
            self._draw_multiline_text(screen)
        else:
            # Single line text drawing
            self._draw_single_line_text(screen)
            
    def _draw_multiline_text(self, screen):
        """Draw multiline text in the text box"""
        # Check if there's any text
        if self.lines == [""] and not self.active:
            # Draw placeholder text for empty text box
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            screen.blit(text_surface, (
                self.rect.x + self.padding['left'],
                self.rect.y + self.padding['top']
            ))
            return
            
        # Calculate visible area
        visible_area = pygame.Rect(
            self.rect.x + self.padding['left'],
            self.rect.y + self.padding['top'],
            self.rect.width - self.padding['left'] - self.padding['right'],
            self.rect.height - self.padding['top'] - self.padding['bottom']
        )
        
        # Create temporary surface for text
        text_surface = pygame.Surface((visible_area.width, max(visible_area.height, len(self.lines) * self.line_height)), 
                                   pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw each line of text
        for i, line in enumerate(self.lines):
            y_pos = i * self.line_height
            
            # Skip lines that are scrolled out of view
            if y_pos < self.scroll_y - self.line_height or y_pos > self.scroll_y + visible_area.height:
                continue
                
            # Draw the line
            if line or i == self.current_line:
                line_surface = self.font.render(line, True, self.text_color)
                text_surface.blit(line_surface, (0, y_pos - self.scroll_y))
            
            # Draw cursor on active line
            if self.active and i == self.current_line and self.cursor_visible:
                cursor_x = self.font.size(line[:self.cursor_pos])[0]
                pygame.draw.line(
                    text_surface,
                    self.text_color,
                    (cursor_x, y_pos - self.scroll_y),
                    (cursor_x, y_pos - self.scroll_y + self.line_height),
                    self.cursor_width
                )
        
        # Blit the text surface to the screen with clipping
        screen.blit(text_surface, visible_area.topleft, 
                  pygame.Rect(0, 0, visible_area.width, visible_area.height))
    
    def _draw_single_line_text(self, screen):
        """Draw single line text in the text box"""
        # Determine what text to display
        display_text = self.text
        
        # For password fields, replace characters with asterisks
        if self.is_password and self.text:
            display_text = '*' * len(self.text)
            
        # Check if there's any text
        if not display_text and not self.active:
            # Draw placeholder text for empty text box
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            text_rect = text_surface.get_rect(
                midleft=(self.rect.x + self.padding['left'], self.rect.centery)
            )
            screen.blit(text_surface, text_rect)
            return
        
        # Create text surface
        text_surface = self.font.render(display_text, True, self.text_color)
        
        # Calculate clipping and scrolling if text is too wide
        max_width = self.rect.width - self.padding['left'] - self.padding['right']
        text_width = text_surface.get_width()
        
        # Determine horizontal scrolling if needed
        scroll_x = 0
        if text_width > max_width:
            # Calculate cursor position in pixels
            cursor_x = self.font.size(display_text[:self.cursor_pos_single])[0]
            
            # Adjust scroll to keep cursor in view
            if cursor_x < scroll_x + self.padding['left']:
                scroll_x = max(0, cursor_x - self.padding['left'])
            elif cursor_x > scroll_x + max_width - self.cursor_width:
                scroll_x = cursor_x - max_width + self.cursor_width
        
        # Create a clipping rect
        clip_rect = pygame.Rect(0, 0, min(text_width, max_width), text_surface.get_height())
        
        # Blit the text with proper positioning
        screen.blit(text_surface, 
                  (self.rect.x + self.padding['left'], self.rect.centery - text_surface.get_height()//2),
                  pygame.Rect(scroll_x, 0, max_width, text_surface.get_height()))
        
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = self.font.size(display_text[:self.cursor_pos_single])[0] - scroll_x + self.rect.x + self.padding['left']
            
            # Make sure cursor stays within text box
            if cursor_x >= self.rect.x + self.padding['left'] and cursor_x <= self.rect.x + self.rect.width - self.padding['right']:
                cursor_y = self.rect.centery - self.line_height//2
                pygame.draw.line(
                    screen,
                    self.text_color,
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.line_height),
                    self.cursor_width
                )
    
    def set_position(self, x, y):
        """Update textbox position with proper alignment"""
        if self.align == "center":
            self.rect.x = x - self.rect.width//2
            self.rect.y = y
        elif self.align == "right":
            self.rect.x = x - self.rect.width
            self.rect.y = y
        else:  # left alignment
            self.rect.x = x
            self.rect.y = y

class Label:
    def __init__(self, x, y, text, color=BLACK, font_size=24, align="center", font_name=None, bold=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.align = align
        
        # Use custom font if provided, otherwise use default
        if font_name:
            self.font = pygame.font.SysFont(font_name, font_size, bold=bold)
        else:
            self.font = pygame.font.SysFont("Arial", font_size, bold=bold)
        
        # Shadow effect for better readability
        self.use_shadow = False
        self.shadow_color = (0, 0, 0, 128)
        self.shadow_offset = 1
        
    def draw(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect()
        
        if self.align == "center":
            text_rect.centerx = self.x
            text_rect.y = self.y
        elif self.align == "right":
            text_rect.right = self.x
            text_rect.y = self.y
        else:  # left alignment
            text_rect.x = self.x
            text_rect.y = self.y
        
        # Draw shadow if enabled
        if self.use_shadow:
            shadow_surf = self.font.render(self.text, True, self.shadow_color)
            shadow_rect = shadow_surf.get_rect(
                x=text_rect.x + self.shadow_offset,
                y=text_rect.y + self.shadow_offset
            )
            screen.blit(shadow_surf, shadow_rect)
            
        screen.blit(text_surf, text_rect)
        
    def set_text(self, text):
        self.text = text
        
    def set_color(self, color):
        self.color = color
        
    def enable_shadow(self, enable=True, color=None, offset=None):
        self.use_shadow = enable
        if color:
            self.shadow_color = color
        if offset:
            self.shadow_offset = offset

class Panel:
    def __init__(self, x, y, width, height, fill_color=LIGHT_GRAY, border_color=None, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.shadow_offset = 5
        self.border_radius = PANEL_RADIUS
        self.use_gradient = True
        
    def draw(self, screen):
        # Draw shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, 
                        pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                        border_radius=self.border_radius)
        screen.blit(shadow_surface, 
                   (self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset))
        
        # Draw main panel with rounded corners
        pygame.draw.rect(screen, self.fill_color, self.rect, border_radius=self.border_radius)
        
        # Draw subtle gradient if enabled
        if self.use_gradient:
            gradient_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            for i in range(self.rect.height // 3):
                alpha = 40 - (i * 1)  # More subtle gradient
                if alpha > 0:
                    pygame.draw.rect(gradient_surface, (255, 255, 255, alpha), 
                                    pygame.Rect(0, i, self.rect.width, 1))
            gradient_rect = gradient_surface.get_rect(topleft=self.rect.topleft)
            screen.blit(gradient_surface, gradient_rect, special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw border if specified
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                           self.border_width, border_radius=self.border_radius)
    
    def set_position(self, x, y):
        """Update panel position"""
        self.rect.x = x
        self.rect.y = y

class ScrollArea:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = 0
        self.scroll_y = 0
        self.max_scroll = 0
        self.scrollbar_width = 10  # Wider scrollbar for better visibility
        self.scrollbar_color = DARK_GRAY
        self.scrollbar_hover_color = PRIMARY
        self.scrollbar_drag_color = PRIMARY_DARK
        self.scrollbar_hovered = False
        self.scrollbar_dragging = False
        self.last_mouse_y = 0
        self.scroll_speed = 40  # Pixels per scroll event
        self.border_radius = 15  # Rounded corners
        
        # New: Enhanced styling properties
        self.shadow_offset = 4
        self.shadow_color = (0, 0, 0, 30)
        self.background_color = LIGHT_GRAY
        self.use_gradient = True
        self.gradient_top = GRADIENT_TOP
        self.gradient_bottom = GRADIENT_BOTTOM
        
    def update(self, content_height):
        self.content_height = content_height
        self.max_scroll = max(0, content_height - self.rect.height)
        self.scroll_y = min(self.scroll_y, self.max_scroll)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.button == 5:  # Scroll down
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                elif self._get_scrollbar_rect().collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    self.last_mouse_y = event.pos[1]
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            self.scrollbar_hovered = self._get_scrollbar_rect().collidepoint(event.pos)
            
            if self.scrollbar_dragging:
                dy = event.pos[1] - self.last_mouse_y
                self.last_mouse_y = event.pos[1]
                
                # Calculate scroll amount based on content and viewport ratio
                scroll_ratio = self.content_height / self.rect.height if self.rect.height > 0 else 1
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + dy * scroll_ratio))
                    
    def _get_scrollbar_rect(self):
        """Returns the rectangle for the scrollbar with smoother sizing"""
        if self.content_height <= self.rect.height:
            return pygame.Rect(0, 0, 0, 0)  # No scrollbar needed
            
        # Calculate scrollbar height (proportional to viewable content)
        scrollbar_height = max(40, int(self.rect.height * (self.rect.height / self.content_height)))
        
        # Calculate scrollbar position
        scrollbar_y_ratio = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0
        scrollbar_y = self.rect.y + (self.rect.height - scrollbar_height) * scrollbar_y_ratio
        
        return pygame.Rect(
            self.rect.right - self.scrollbar_width - 5,  # Slightly inset from edge
            scrollbar_y,
            self.scrollbar_width,
            scrollbar_height
        )
        
    def get_scroll_offset(self):
        return self.scroll_y
        
    def get_clip_rect(self):
        return self.rect
        
    def draw(self, screen):
        # Draw background with gradient
        if self.use_gradient:
            gradient_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            for i in range(self.rect.height):
                alpha = int(255 * (1 - i / self.rect.height))
                color = (
                    int(self.gradient_top[0] + (self.gradient_bottom[0] - self.gradient_top[0]) * (i / self.rect.height)),
                    int(self.gradient_top[1] + (self.gradient_bottom[1] - self.gradient_top[1]) * (i / self.rect.height)),
                    int(self.gradient_top[2] + (self.gradient_bottom[2] - self.gradient_top[2]) * (i / self.rect.height)),
                    alpha
                )
                pygame.draw.line(gradient_surface, color, (0, i), (self.rect.width, i))
            screen.blit(gradient_surface, self.rect)
        else:
            pygame.draw.rect(screen, self.background_color, self.rect, border_radius=self.border_radius)
        
        # Draw shadow
        if self.shadow_offset > 0:
            shadow_rect = pygame.Rect(
                self.rect.x + self.shadow_offset,
                self.rect.y + self.shadow_offset,
                self.rect.width,
                self.rect.height
            )
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, self.shadow_color, 
                            pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                            border_radius=self.border_radius)
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw scrollbar if needed
        if self.content_height > self.rect.height:
            scrollbar_rect = self._get_scrollbar_rect()
            
            # Draw scrollbar track
            track_rect = pygame.Rect(
                self.rect.right - self.scrollbar_width - 5,
                self.rect.y,
                self.scrollbar_width,
                self.rect.height
            )
            pygame.draw.rect(screen, (200, 200, 200), track_rect, border_radius=self.border_radius)
            
            # Draw scrollbar thumb
            thumb_color = self.scrollbar_drag_color if self.scrollbar_dragging else (
                self.scrollbar_hover_color if self.scrollbar_hovered else self.scrollbar_color
            )
            pygame.draw.rect(screen, thumb_color, scrollbar_rect, border_radius=self.border_radius)
            
    def set_position(self, x, y):
        """Update scroll area position"""
        self.rect.x = x
        self.rect.y = y