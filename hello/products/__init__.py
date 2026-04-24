from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required
from sqlalchemy import or_
import csv
import io
from datetime import datetime

from hello.models import Product
from hello.extensions import db
from hello.initializers import redis

products = Blueprint("products", __name__, template_folder="templates", url_prefix="/products")

EXPORT_COLUMNS = [
    ("id", "ID"),
    ("name", "商品名称"),
    ("sku", "SKU"),
    ("category", "分类"),
    ("price", "价格"),
    ("stock", "库存"),
    ("status", "状态"),
    ("description", "描述"),
    ("created_at", "创建时间"),
    ("updated_at", "更新时间"),
]

EXPORT_RATE_LIMIT_SECONDS = 60


def check_rate_limit(user_id):
    key = f"export:rate_limit:{user_id}"
    if redis.exists(key):
        return False
    redis.setex(key, EXPORT_RATE_LIMIT_SECONDS, "1")
    return True


def build_query(filters=None):
    query = Product.query

    if filters:
        keyword = filters.get("keyword")
        category = filters.get("category")
        status = filters.get("status")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")

        if keyword:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{keyword}%"),
                    Product.sku.ilike(f"%{keyword}%"),
                    Product.description.ilike(f"%{keyword}%"),
                )
            )

        if category:
            query = query.filter(Product.category == category)

        if status:
            query = query.filter(Product.status == status)

        if min_price:
            query = query.filter(Product.price >= float(min_price))

        if max_price:
            query = query.filter(Product.price <= float(max_price))

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(Product.created_at >= start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Product.created_at <= end_dt)
            except ValueError:
                pass

    return query


@products.route("/")
@login_required
def list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    filters = {
        "keyword": request.args.get("keyword", ""),
        "category": request.args.get("category", ""),
        "status": request.args.get("status", ""),
        "min_price": request.args.get("min_price", ""),
        "max_price": request.args.get("max_price", ""),
        "start_date": request.args.get("start_date", ""),
        "end_date": request.args.get("end_date", ""),
    }

    query = build_query(filters)

    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "products/list.html",
        products=pagination.items,
        pagination=pagination,
        filters=filters,
        categories=categories,
        columns=EXPORT_COLUMNS,
    )


@products.route("/api/list")
@login_required
def api_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    filters = {
        "keyword": request.args.get("keyword", ""),
        "category": request.args.get("category", ""),
        "status": request.args.get("status", ""),
        "min_price": request.args.get("min_price", ""),
        "max_price": request.args.get("max_price", ""),
        "start_date": request.args.get("start_date", ""),
        "end_date": request.args.get("end_date", ""),
    }

    query = build_query(filters)
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })


def generate_csv(filters):
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [col[1] for col in EXPORT_COLUMNS]
    writer.writerow(headers)
    yield output.getvalue()
    output.seek(0)
    output.truncate()

    query = build_query(filters)
    query = query.order_by(Product.created_at.desc())

    batch_size = 1000
    page = 1

    while True:
        pagination = query.paginate(page=page, per_page=batch_size, error_out=False)
        items = pagination.items

        if not items:
            break

        for product in items:
            row = []
            for key, _ in EXPORT_COLUMNS:
                value = getattr(product, key)
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S") if value else ""
                elif value is None:
                    value = ""
                row.append(str(value))
            writer.writerow(row)
            yield output.getvalue()
            output.seek(0)
            output.truncate()

        page += 1


@products.route("/api/export/csv")
@login_required
def export_csv():
    from flask_login import current_user

    if not check_rate_limit(current_user.id):
        return jsonify({
            "error": "请求过于频繁，请稍后再试（同一用户1分钟内只能导出一次）"
        }), 429

    filters = {
        "keyword": request.args.get("keyword", ""),
        "category": request.args.get("category", ""),
        "status": request.args.get("status", ""),
        "min_price": request.args.get("min_price", ""),
        "max_price": request.args.get("max_price", ""),
        "start_date": request.args.get("start_date", ""),
        "end_date": request.args.get("end_date", ""),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"products_export_{timestamp}.csv"

    response = Response(
        generate_csv(filters),
        mimetype="text/csv; charset=utf-8",
    )
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response
