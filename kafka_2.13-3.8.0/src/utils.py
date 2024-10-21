import numpy as np
import cv2
# import matplotlib.pyplot as plt


np.random.seed(3)

# def show_mask(mask, ax, random_color=False, borders = True):
#     if random_color:
#         color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
#     else:
#         color = np.array([30/255, 144/255, 255/255, 0.6])
#     h, w = mask.shape[-2:]
#     mask = mask.astype(np.uint8)
#     mask_image =  mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
#     if borders:
#         import cv2
#         contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
#         # Try to smooth contours
#         contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
#         mask_image = cv2.drawContours(mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2) 
#     ax.imshow(mask_image)

# def show_points(coords, labels, ax, marker_size=375):
#     pos_points = coords[labels==1]
#     neg_points = coords[labels==0]
#     ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
#     ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   

# def show_box(box, ax):
#     x0, y0 = box[0], box[1]
#     w, h = box[2] - box[0], box[3] - box[1]
#     ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))    

# def show_masks(image, masks, scores, point_coords=None, box_coords=None, input_labels=None, borders=True):
#     for i, (mask, score) in enumerate(zip(masks, scores)):
#         plt.figure(figsize=(10, 10))
#         plt.imshow(image)
#         show_mask(mask, plt.gca(), borders=borders)
#         if point_coords is not None:
#             assert input_labels is not None
#             show_points(point_coords, input_labels, plt.gca())
#         if box_coords is not None:
#             # boxes
#             show_box(box_coords, plt.gca())
#         if len(scores) > 1:
#             plt.title(f"Mask {i+1}, Score: {score:.3f}", fontsize=18)
#         plt.axis('off')
#         plt.show()
        
def get_mask_image(image, masks, scores, point_coords=None, box_coords=None, input_labels=None, borders=True):
    masked_image = image.copy()  # Create a copy of the image to modify

    for i, (mask, score) in enumerate(zip(masks, scores)):
        # Convert the mask to the same size as the image
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        # Create a colored overlay for the mask
        color_mask = np.zeros_like(image)
        color = np.random.randint(0, 256, size=3).tolist()  # Random color for each mask
        color_mask[mask > 0.5] = color  # Apply color to the mask

        # Blend the mask onto the image
        alpha = 0.5  # Transparency factor
        masked_image = cv2.addWeighted(masked_image, 1 - alpha, color_mask, alpha, 0)

        # Optional: Draw points if provided
        if point_coords is not None and input_labels is not None:
            for point, label in zip(point_coords, input_labels):
                cv2.circle(masked_image, tuple(point), radius=5, color=(0, 255, 0), thickness=-1)

        # Optional: Draw boxes if provided
        if box_coords is not None:
            for box in box_coords:
                cv2.rectangle(masked_image, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 2)

    return masked_image
