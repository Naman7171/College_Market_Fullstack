from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Listing, ListingImage, User
from database import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

marketplace_bp = Blueprint('marketplace', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@marketplace_bp.route('/listings', methods=['GET'])
def get_listings():
    try:
        # Get query parameters
        category = request.args.get('category')
        condition = request.args.get('condition')
        min_price = request.args.get('minPrice', type=float)
        max_price = request.args.get('maxPrice', type=float)
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Build query
        query = Listing.query

        if category:
            query = query.filter(Listing.category == category)
        if condition:
            query = query.filter(Listing.condition == condition)
        if min_price is not None:
            query = query.filter(Listing.price >= min_price)
        if max_price is not None:
            query = query.filter(Listing.price <= max_price)
        if search:
            search = f"%{search}%"
            query = query.filter(
                (Listing.title.ilike(search)) | 
                (Listing.description.ilike(search))
            )

        # Get paginated results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        listings = pagination.items

        # Format response
        listings_data = []
        for listing in listings:
            listing_data = {
                'id': listing.id,
                'title': listing.title,
                'description': listing.description,
                'price': float(listing.price),
                'category': listing.category,
                'condition': listing.condition,
                'image_url': listing.images[0].url if listing.images else None,
                'seller_id': listing.seller_id,
                'created_at': listing.created_at.isoformat(),
                'updated_at': listing.updated_at.isoformat(),
                'seller': {
                    'id': listing.seller.id,
                    'username': listing.seller.username,
                    'email': listing.seller.email
                }
            }
            listings_data.append(listing_data)

        return jsonify({
            'listings': listings_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings', methods=['POST'])
@jwt_required()
def create_listing():
    try:
        current_user_id = get_jwt_identity()
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        condition = request.form.get('condition')
        images = request.files.getlist('images')

        # Validate required fields
        if not title or not description or not price or not category or not condition:
            return jsonify({'error': 'All fields are required'}), 422

        # Validate price
        try:
            price = float(price)
            if price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 422
        except ValueError:
            return jsonify({'error': 'Price must be a valid number'}), 422

        # Validate images
        if not images or len(images) == 0:
            return jsonify({'error': 'At least one image is required'}), 422

        # Create listing
        listing = Listing(
            title=title,
            description=description,
            price=price,
            category=category,
            condition=condition,
            seller_id=current_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(listing)
        db.session.flush()  # Get the listing ID

        # Handle image uploads
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                # Create uploads directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image.save(filepath)
                
                # Create image record
                listing_image = ListingImage(
                    listing_id=listing.id,
                    url=f'/uploads/{filename}',
                    created_at=datetime.utcnow()
                )
                db.session.add(listing_image)
            else:
                db.session.rollback()
                return jsonify({'error': 'Invalid image file type'}), 422

        db.session.commit()

        return jsonify({
            'message': 'Listing created successfully',
            'listing_id': listing.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings/<int:listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)

        # Check if user owns the listing
        if listing.seller_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Update fields
        if 'title' in request.form:
            listing.title = request.form['title']
        if 'description' in request.form:
            listing.description = request.form['description']
        if 'price' in request.form:
            listing.price = float(request.form['price'])
        if 'category' in request.form:
            listing.category = request.form['category']
        if 'condition' in request.form:
            listing.condition = request.form['condition']

        listing.updated_at = datetime.utcnow()

        # Handle image updates
        images = request.files.getlist('images')
        if images:
            # Delete existing images
            ListingImage.query.filter_by(listing_id=listing_id).delete()
            
            # Add new images
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(filepath)
                    
                    listing_image = ListingImage(
                        listing_id=listing.id,
                        url=f'/uploads/{filename}',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(listing_image)

        db.session.commit()

        return jsonify({'message': 'Listing updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings/<int:listing_id>', methods=['DELETE'])
@jwt_required()
def delete_listing(listing_id):
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)

        # Check if user owns the listing
        if listing.seller_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Delete associated images
        for image in listing.images:
            # Delete the file
            filepath = os.path.join(UPLOAD_FOLDER, image.url.split('/')[-1])
            if os.path.exists(filepath):
                os.remove(filepath)
            # Delete the database record
            db.session.delete(image)

        # Delete the listing
        db.session.delete(listing)
        db.session.commit()

        return jsonify({'message': 'Listing deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    try:
        listing = Listing.query.get_or_404(listing_id)
        
        listing_data = {
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'price': float(listing.price),
            'category': listing.category,
            'condition': listing.condition,
            'image_urls': [img.url for img in listing.images],
            'seller_id': listing.seller_id,
            'created_at': listing.created_at.isoformat(),
            'updated_at': listing.updated_at.isoformat(),
            'seller': {
                'id': listing.seller.id,
                'username': listing.seller.username,
                'email': listing.seller.email
            }
        }

        return jsonify(listing_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
