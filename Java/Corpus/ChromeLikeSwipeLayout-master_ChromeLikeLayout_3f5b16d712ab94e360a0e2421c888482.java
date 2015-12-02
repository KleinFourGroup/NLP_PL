package com.asha;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.support.v4.view.ViewCompat;
import android.support.v4.view.animation.FastOutSlowInInterpolator;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.Animation;
import android.view.animation.BounceInterpolator;
import android.view.animation.Transformation;

import com.asha.ChromeLikeSwipeLayout.IOnExpandViewListener;

import java.util.List;

import static com.asha.ChromeLikeSwipeLayout.dp2px;


/**
 * Created by hzqiujiadi on 15/11/18.
 * hzqiujiadi ashqalcn@gmail.com
 */
public class ChromeLikeLayout extends ViewGroup implements IOnExpandViewListener {
    private static final String TAG = "ChromeLikeView";
    private static final float sMagicNumber = 0.55228475f;
    private static final int sDefaultCircleColor = 0xFFFFCC11;
    private Paint mPaint;
    private Path mPath;
    private float mPrevX;
    private float mDegrees;
    private boolean mIsFirstExpanded;
    private float mTranslate;
    private int mCurrentFlag;
    private int mRadius = dp2px(40);
    private int mGap = dp2px(15);
    private IOnRippleListener mRippleListener;
    private GummyAnimatorHelper mGummyAnimatorHelper = new GummyAnimatorHelper();
    private RippleAnimatorHelper mRippleAnimatorHelper = new RippleAnimatorHelper();

    public ChromeLikeLayout(Context context) {
        this(context,null);
    }

    public ChromeLikeLayout(Context context, AttributeSet attrs) {
        this(context, attrs,0);
    }

    public ChromeLikeLayout(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private int getItemWidth(){
        return mRadius*2 + mGap;
    }

    private int getCircleStartX(){
        int contentWidth = getItemWidth();
        int totalWidth = getMeasuredWidth();
        int totalContextWidth = contentWidth * (getChildCount() - 1);
        return (totalWidth - totalContextWidth) >> 1;
    }

    @Override
    protected void onLayout(boolean changed, int l, int t, int r, int b) {

        int startXOffset = getCircleStartX();
        int startYOffset = (b - t);

        for (int i = 0 ; i < getChildCount() ; i++ ){
            View view = getChildAt(i);
            final int left = startXOffset + i * getItemWidth() - view.getMeasuredWidth()/2;
            final int right = left + view.getMeasuredWidth();
            final int top = (startYOffset - view.getMeasuredHeight())>>1;
            final int bottom = top + view.getMeasuredHeight();
            view.layout(left,top,right,bottom);
        }
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec);
        measureChildren(getMeasuredWidth(),getMeasuredHeight());
    }

    private void init() {

        setBackgroundColor(0xFF333333);

        mPaint = new Paint();
        mPaint.setColor(sDefaultCircleColor);
        mPaint.setStyle(Paint.Style.FILL);
        mPaint.setAntiAlias(true);

        mPath = new Path();
        reset();
        setWillNotDraw(false);
    }

    public void setIcons(List<Integer> drawables){
        this.removeAllViews();
        for ( int res : drawables ){
            View v = new View(getContext());
            v.setBackgroundResource(res);
            addView(v, LayoutParams.WRAP_CONTENT,LayoutParams.WRAP_CONTENT);
        }
    }

    public void setRadius(int radius) {
        this.mRadius = radius;
    }

    public void onActionDown(){
        reset();
    }

    public void onActionMove(MotionEvent event, boolean isExpanded){
        if ( !mIsFirstExpanded && isExpanded ){
            mIsFirstExpanded = true;
            mPrevX = event.getX();
            return;
        }

        if ( !isExpanded ) return;

        if ( !isBesselEnable() ){
            updateAlpha(1);
            updatePath( mPrevX, mPrevX, mRadius, false );
            return;
        }

        float currentX = event.getX();
        if ( mGummyAnimatorHelper.isAnimationStarted() ){
            mGummyAnimatorHelper.updateFromX(currentX);
            return;
        }

        updateAlpha(1);
        updatePath( currentX, mPrevX, mRadius, false );
        if ( Math.abs( currentX - mPrevX ) > getItemWidth() * 0.5 ){
            if ( currentX > mPrevX ) updateCurrentFlag(nextOfCurrentFlag());
            else updateCurrentFlag(prevOfCurrentFlag());
            mGummyAnimatorHelper.launchAnim(
                    currentX
                    , mPrevX
                    , mTranslate
                    , flag2TargetTranslate() );
        }
    }

    public void onActionUpOrCancel(boolean isExpanded){
        if ( !mIsFirstExpanded ) return;
        mIsFirstExpanded = false;
        boolean isRippleAnimEnabled = getChildCount() > 0;
        if ( isExpanded ){
            if ( isRippleAnimEnabled ){
                if ( mRippleAnimatorHelper.isAnimationStarted() ) return;
                mRippleAnimatorHelper.launchAnim(mRadius,getMeasuredWidth());
            } else {
                if ( mRippleListener != null ) mRippleListener.onRippleAnimFinished(-1);
            }

        }
    }

    private void reset(){
        onExpandView(0,false);
        updateAlpha(1);
        updateCurrentFlag((getChildCount() - 1) >> 1);
        mTranslate = flag2TargetTranslate();
    }

    private boolean isBesselEnable(){
        return getChildCount() > 1;
    }

    private void updateAlpha( float alpha ){
        mPaint.setAlpha(Math.round(255 * alpha));
    }

    private void updatePath(float currentX, float prevX, int radius, boolean animate){
        updatePath(currentX,0,prevX,0,radius,animate);
    }

    private void updatePath(float currentX, float currentY, float prevX, float prevY, int radius, boolean animate ){
        float distance = distance(prevX, prevY, currentX, currentY);
        float tempDegree = points2Degrees(prevX, prevY, currentX, currentY);
        if ( animate ){
            if ( Math.abs( mDegrees - tempDegree ) > 5 ) distance = -distance;
        } else {
            //if ( distance < mTouchSlop ) distance = 0;
            mDegrees = tempDegree;
        }
        float realLong = radius + distance;
        float realShort = radius - distance * 0.1f;

        mPath.reset();

        mPath.lineTo(0, -radius);
        mPath.cubicTo(radius * sMagicNumber, -radius
                , realLong, -radius * sMagicNumber
                , realLong, 0);
        mPath.lineTo(0, 0);

        mPath.lineTo(0, radius);
        mPath.cubicTo(radius * sMagicNumber, radius
                , realLong, radius * sMagicNumber
                , realLong, 0);
        mPath.lineTo(0, 0);

        mPath.lineTo(0, -radius);
        mPath.cubicTo(-radius * sMagicNumber, -radius
                , -realShort, -radius * sMagicNumber
                , -realShort, 0);
        mPath.lineTo(0, 0);

        mPath.lineTo(0, radius);
        mPath.cubicTo(-radius * sMagicNumber, radius
                , -realShort, radius * sMagicNumber
                , -realShort, 0);
        mPath.lineTo(0, 0);

        //postInvalidate();
        invalidate();
    }

    private void updateIconScale( float fraction ){
        float iconFraction = iconOffsetFraction(fraction);
        for (int i = 0 ; i < getChildCount(); i++ ){
            View v = getChildAt(i);
            ViewCompat.setScaleX(v,iconFraction);
            ViewCompat.setScaleY(v,iconFraction);
        }
    }

    private void updateCurrentFlag(int flag){
        mCurrentFlag = flag;
        boolean isPressed;
        for (int i = 0 ; i < getChildCount() ; i++ ){
            View view = getChildAt(i);
            isPressed = i == mCurrentFlag;
            view.setPressed(isPressed);
        }
    }

    private int nextOfCurrentFlag(){
        int tmp = mCurrentFlag;
        tmp++;
        tmp %= getChildCount();
        return tmp;
    }

    private int prevOfCurrentFlag(){
        int tmp = mCurrentFlag;
        tmp--;
        tmp += getChildCount();
        tmp %= getChildCount();
        return tmp;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        if ( getChildCount() == 0 ) return;
        int centerY = getMeasuredHeight() >> 1;

        canvas.save();
        canvas.translate(mTranslate, centerY);
        canvas.rotate(mDegrees);
        canvas.drawPath(mPath, mPaint);
        canvas.restore();
    }

    private static float distance(float x1,float y1, float x2, float y2){
        return (float) Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2));
    }
    private int flag2TargetTranslate(){
        int startXOffset = getCircleStartX();
        return startXOffset + getItemWidth() * mCurrentFlag;
    }

    private static float points2Degrees(float x1, float y1, float x2, float y2){
        double angle = Math.atan2(y2-y1,x2-x1);
        return (float) Math.toDegrees(angle);
    }

    @Override
    public void onExpandView(float fraction, boolean isFromCancel) {
        float circleFraction = circleOffsetFraction(fraction);
        if (isFromCancel) updateAlpha(circleFraction);
        updatePath(0,0,Math.round(mRadius*circleFraction),true);
        updateIconScale(fraction);
    }

    private static final float factorScaleCircle = 0.75f;
    private static final float factorScaleIcon = 0.3f;

    private float circleOffsetFraction( float fraction ){
        return offsetFraction(fraction,factorScaleCircle);
    }

    private float iconOffsetFraction( float fraction ){
        return offsetFraction(fraction,factorScaleIcon);
    }

    private float offsetFraction(float fraction, float factor){
        float result = (fraction - factor) / (1 - factor);
        result = result > 0 ? result : 0;
        return result;
    }

    public void setRippleListener(IOnRippleListener mRippleListener) {
        this.mRippleListener = mRippleListener;
    }

    public void setCircleColor(int circleColor) {
        mPaint.setColor(circleColor);
    }

    public void setGap(int gap) {
        this.mGap = gap;
    }

    public interface IOnRippleListener {
        void onRippleAnimFinished(int index);
    }

    public class RippleAnimatorHelper implements Animation.AnimationListener {

        private float mAnimFromRadius;
        private float mAnimToRadius;
        private boolean mAnimationStarted;
        private boolean mEventDispatched;


        public void onAnimationUpdate(float interpolation) {
            int currentRadius = FloatEvaluator.evaluate(interpolation,mAnimFromRadius,mAnimToRadius).intValue();
            updatePath(0, 0, currentRadius, true);
            updateAlpha(1-interpolation);
        }

        public void launchAnim(float fromRadius, float toRadius) {

            mAnimFromRadius = fromRadius;
            mAnimToRadius = toRadius;
            Animation animation = new Animation() {
                @Override
                protected void applyTransformation(float interpolatedTime, Transformation t) {
                    onAnimationUpdate(interpolatedTime);
                }
            };
            animation.setDuration(300);
            animation.setInterpolator(new FastOutSlowInInterpolator());
            animation.setAnimationListener(this);
            View target = ChromeLikeLayout.this.getChildAt(mCurrentFlag);
            target.clearAnimation();
            target.startAnimation(animation);
        }

        public boolean isAnimationStarted() {
            return mAnimationStarted;
        }

        @Override
        public void onAnimationStart(Animation animation) {
            mAnimationStarted = true;
            mEventDispatched = false;
        }

        @Override
        public void onAnimationEnd(Animation animation) {
            mAnimationStarted = false;
            if ( !mEventDispatched && mRippleListener != null ){
                mRippleListener.onRippleAnimFinished(mCurrentFlag);
                mEventDispatched = true;
            }
        }

        @Override
        public void onAnimationRepeat(Animation animation) {

        }
    }


    public class GummyAnimatorHelper implements Animation.AnimationListener   {

        private float mAnimFromX;
        private float mAnimToX;
        private float mAnimFromTranslate;
        private float mAnimToTranslate;
        private boolean mAnimationStarted;


        public void onAnimationUpdate(float interpolation) {
            Float currentX = FloatEvaluator.evaluate(interpolation,mAnimFromX,mAnimToX);
            mTranslate = FloatEvaluator.evaluate(interpolation, mAnimFromTranslate, mAnimToTranslate);
            updatePath(currentX, mAnimToX, mRadius, true);
        }

        public void launchAnim(float fromX, float toX, float fromTranslate, float toTranslate) {

            mAnimFromX = fromX;
            mAnimToX = toX;
            mAnimFromTranslate = fromTranslate;
            mAnimToTranslate = toTranslate;

            Animation animation = new Animation() {
                @Override
                protected void applyTransformation(float interpolatedTime, Transformation t) {
                    onAnimationUpdate(interpolatedTime);
                }
            };
            animation.setDuration(200);
            animation.setInterpolator(new BounceInterpolator());
            animation.setAnimationListener(this);
            ChromeLikeLayout.this.clearAnimation();
            ChromeLikeLayout.this.startAnimation(animation);
        }

        public boolean isAnimationStarted() {
            return mAnimationStarted;
        }

        public void updateFromX(float currentX) {
            mAnimFromX = currentX;
        }

        @Override
        public void onAnimationStart(Animation animation) {
            mAnimationStarted = true;
        }

        @Override
        public void onAnimationEnd(Animation animation) {
            mAnimationStarted = false;
            mPrevX = mAnimFromX;
        }

        @Override
        public void onAnimationRepeat(Animation animation) {

        }
    }

    public static class FloatEvaluator {

        public static Float evaluate(float fraction, Number startValue, Number endValue) {
            float startFloat = startValue.floatValue();
            return startFloat + fraction * (endValue.floatValue() - startFloat);
        }
    }
}
