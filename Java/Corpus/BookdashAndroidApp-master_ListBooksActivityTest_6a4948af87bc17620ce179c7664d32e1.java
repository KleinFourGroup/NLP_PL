package org.bookdash.android.presentation.listbooks;

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
import org.bookdash.android.data.settings.FakeSettingsApiImpl;
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


import static android.support.test.espresso.assertion.ViewAssertions.doesNotExist;
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
 * @since 15/11/14.
 */
@RunWith(AndroidJUnit4.class)
@LargeTest
public class ListBooksActivityTest {

    @Rule
    public ActivityTestRule<ListBooksActivity> activityTestRule =
            new ActivityTestRule<>(ListBooksActivity.class);

    @Before
    public void setUp() {
        Intents.init();
        FakeSettingsApiImpl.setLanguagePref("English");
    }

    @After
    public void tearDown() {
        Intents.release();
        FakeSettingsApiImpl.setLanguagePref("English");
    }


    @Test
    public void loadBooks_BookTitlesVisible() {
        //When
        //AUTOMATIC LAUNCH OF ACTIVITY

        //Then
        onView(withText("Searching for Spring")).check(matches(isDisplayed()));
        onView(withText("Why is Nita Upside Down?")).check(matches(isDisplayed()));
    }

    @Test
    public void clickOnBook_OpensBookDetails() {
        //When
        onView(withText("Searching for Spring")).perform(click());
        //Then
        intended(hasComponent(BookInfoActivity.class.getName()));

    }

    @Test
    public void openScreen_AppBarTitleIsCorrect() {
        matchToolbarTitle("Book Dash");
    }

    @Test
    public void chooseDifferentLanguage_NewBooksLoaded(){
        openActionBarOverflowOrOptionsMenu(InstrumentationRegistry.getTargetContext());
        String title = InstrumentationRegistry.getTargetContext().getString(R.string.action_language_choice);
        onView(withText(title)).perform(click());

        //When
        onView(withText("Zulu")).perform(click());

        //Then
        onView(withText("[ZULU]isipilingi")).check(matches(isDisplayed()));
        onView(withText("Searching for Spring")).check(doesNotExist());
        onView(withText("[ZULU]kubheke phansi")).check(matches(isDisplayed()));
        onView(withText("Why is Nita Upside Down?")).check(doesNotExist());
    }




    private static ViewInteraction matchToolbarTitle(
            CharSequence title) {
        return onView(isAssignableFrom(Toolbar.class))
                .check(matches(withToolbarTitle(is(title))));
    }

    //Custom matchers are used so that we can reuse matching in other tests.
    private static Matcher<Object> withToolbarTitle(
            final Matcher<CharSequence> textMatcher) {
        return new BoundedMatcher<Object, Toolbar>(Toolbar.class) {
            @Override
            public boolean matchesSafely(Toolbar toolbar) {
                return textMatcher.matches(toolbar.getTitle());
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("with toolbar title: ");
                textMatcher.describeTo(description);
            }
        };
    }

}
