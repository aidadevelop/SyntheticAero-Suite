import cv2
import numpy as np

class AnnotationUtils:
    """Утилиты для аннотаций"""
    
    @staticmethod
    def points_to_mask(points, image_shape):
        """Преобразование точек в маску"""
        img_height, img_width = image_shape
        mask = np.zeros((img_height, img_width), dtype=np.uint8)
        
        if len(points) >= 3:
            pts = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    @staticmethod
    def draw_annotations(image, annotations, canvas_scale, class_colors):
        """Отрисовка аннотаций на изображении"""
        display_image = image.copy()
        
        for i, ann in enumerate(annotations):
            color = class_colors.get(ann['class'], (255, 255, 255))
            
            if ann['type'] == 'manual':
                
                for point in ann['points']:
                    scaled_point = (int(point[0] * canvas_scale), 
                                  int(point[1] * canvas_scale))
                    cv2.circle(display_image, scaled_point, 3, color, -1)
                    cv2.circle(display_image, scaled_point, 5, (255, 255, 255), 1)
            
            elif 'mask' in ann and ann['mask'] is not None:
                
                mask = cv2.resize(ann['mask'].astype(np.uint8), 
                                (image.shape[1], image.shape[0]))
                colored_mask = np.zeros_like(display_image)
                colored_mask[mask > 0] = color
                display_image = cv2.addWeighted(display_image, 0.7, colored_mask, 0.3, 0)
                
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(display_image, contours, -1, color, 2)
        
        return display_image
    
    @staticmethod
    def draw_manual_points(image, manual_points, canvas_scale):
        """Отрисовка текущих точек пользователя"""
        display_image = image.copy()
        
        for point in manual_points:
            if len(point) == 3:  
                x, y, label = point
                color = (0, 255, 0) if label == 1 else (255, 0, 0)
            else:  
                x, y = point
                color = (0, 255, 0)
            
            scaled_point = (int(x * canvas_scale), int(y * canvas_scale))
            cv2.circle(display_image, scaled_point, 4, color, -1)
            cv2.circle(display_image, scaled_point, 6, (255, 255, 255), 2)
        
        return display_image