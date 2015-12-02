package org.bookdash.android.presentation.readbook;

import android.support.v4.app.FixedFragmentStatePagerAdapter;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;

import org.bookdash.android.domain.pojo.gson.Page;

import java.util.List;

/**
 * @author Rebecca Franks (rebecca.franks@dstvdm.com)
 * @since 2015/07/22 7:21 PM
 */
public class PageAdapter extends FixedFragmentStatePagerAdapter {

    private final String rootFileLocation;
    private List<Page> pages;


    public PageAdapter(FragmentManager fm, List<Page> pages, String rootFileLocation) {
        super(fm);
        this.pages = pages;
        this.rootFileLocation = rootFileLocation;
    }

    @Override
    public Fragment getItem(int position) {
        int realPos = position * 2;
        Page page = pages.get(realPos);
        Page page2 = null;
        if ( realPos + 1 < pages.size()){
            page2 = pages.get(realPos + 1);
        }
        return PageFragment.newInstance(page, page2,rootFileLocation);
    }


    @Override
    public int getCount() {
        return (int) Math.ceil(((float) this.pages.size()) / 2.0f);
    }

}

