package org.bookdash.android.presentation.bookinfo;

import android.content.Intent;
import android.support.test.espresso.intent.Intents;
import android.support.test.espresso.matcher.ViewMatchers;
import android.support.test.rule.ActivityTestRule;
import android.support.test.runner.AndroidJUnit4;
import android.test.suitebuilder.annotation.LargeTest;

import org.bookdash.android.domain.pojo.BookDetailParcelable;
import org.bookdash.android.presentation.listbooks.BookViewHolder;
import org.bookdash.android.presentation.listbooks.ListBooksActivity;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.support.test.InstrumentationRegistry;
import android.support.test.espresso.ViewInteraction;
import android.support.test.espresso.intent.Intents;
import android.support.test.espresso.matcher.BoundedMatcher;
import android.support.test.rule.ActivityTestRule;
import android.support.test.runner.AndroidJUnit4;
import android.support.v7.widget.Toolbar;
import android.test.suitebuilder.annotation.LargeTest;
import android.view.MenuItem;

import org.bookdash.android.R;
import org.bookdash.android.presentation.about.AboutActivity;
import org.bookdash.android.presentation.bookinfo.BookInfoActivity;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.bookdash.android.mock.test.BuildConfig;


import static android.support.test.espresso.matcher.ViewMatchers.isAssignableFrom;
import static android.support.test.espresso.Espresso.*;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.intent.Intents.intended;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasAction;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasComponent;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasData;
import static android.support.test.espresso.matcher.RootMatchers.isDialog;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withEffectiveVisibility;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasAction;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasData;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.Matchers.contains;


import static android.support.test.espresso.intent.Intents.intended;
import static android.support.test.espresso.intent.matcher.IntentMatchers.hasComponent;

/**
 * @author rebeccafranks
 * @since 15/11/21.
 */
@RunWith(AndroidJUnit4.class)
@LargeTest
public class BookInfoActivityTest {

    @Rule
    public ActivityTestRule<BookInfoActivity> activityTestRule =
            new ActivityTestRule<>(BookInfoActivity.class, true, false);

    @Before
    public void setUp() {
        Intents.init();
    }

    @After
    public void tearDown() {
        Intents.release();
    }
    public static final String BOOK_OBJ_ID = "f4r2gho2h";

    @Test
    public void loadBookInfo_DisplayBookInformation(){
        Intent intent = new Intent();
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        BookDetailParcelable bookDetailParcelable = new BookDetailParcelable();
        bookDetailParcelable.setBookDetailObjectId(BOOK_OBJ_ID);
        bookDetailParcelable.setBookTitle("Searching for Spring");
        bookDetailParcelable.setBookImageUrl("http://riggaroo.co.za/bookdash/3-fishgift/xhosa/1-cover.jpg");
        intent.putExtra(BookInfoActivity.BOOK_PARCEL, bookDetailParcelable);
        activityTestRule.launchActivity(intent);

        onView(withText("Searching for Spring")).check(matches(withEffectiveVisibility(ViewMatchers.Visibility.VISIBLE)));

        onView(withText("Rebecca Franks")).check(matches(withEffectiveVisibility(ViewMatchers.Visibility.VISIBLE)));
        onView(withText("Johan Smith")).check(matches(withEffectiveVisibility(ViewMatchers.Visibility.VISIBLE)));
    }
}
